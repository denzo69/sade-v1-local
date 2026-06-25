from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import json
import uuid


TASKS_FILENAME = "tasks.json"
TASK_HISTORY_FILENAME = "task_history.jsonl"
VALID_STATUSES = {"queued", "running", "done", "failed", "cancelled"}


def _memory_path(project_path: Path) -> Path:
    path = project_path / "memory"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _tasks_path(project_path: Path) -> Path:
    return _memory_path(project_path) / TASKS_FILENAME


def _history_path(project_path: Path) -> Path:
    return _memory_path(project_path) / TASK_HISTORY_FILENAME


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _load_tasks(project_path: Path) -> List[Dict[str, Any]]:
    path = _tasks_path(project_path)
    if not path.exists():
        path.write_text("[]", encoding="utf-8")
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    return data if isinstance(data, list) else []


def _save_tasks(project_path: Path, tasks: List[Dict[str, Any]]) -> None:
    _tasks_path(project_path).write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")


def _append_history(project_path: Path, entry: Dict[str, Any]) -> None:
    item = {"time": _now(), **entry}
    with _history_path(project_path).open("a", encoding="utf-8") as file:
        file.write(json.dumps(item, ensure_ascii=False) + "\n")


def _preview(value: Any, max_chars: int = 2500) -> Any:
    if isinstance(value, str):
        return value if len(value) <= max_chars else value[:max_chars].rstrip() + f"... [katkaistu, alkuperäinen pituus {len(value)} merkkiä]"
    if isinstance(value, dict):
        safe: Dict[str, Any] = {}
        for key, item in value.items():
            safe[key] = _preview(item, 900 if str(key).lower() in {"reply", "content", "text", "prompt"} else max_chars)
        return safe
    if isinstance(value, list):
        return [_preview(item, max_chars=max_chars) for item in value[:50]]
    return value


def add_task(project_path: Path, prompt: str, title: Optional[str] = None, tags: Optional[List[str]] = None, priority: int = 3) -> Dict[str, Any]:
    clean_prompt = prompt.strip()
    if not clean_prompt:
        return {"ok": False, "message": "Tehtävän prompt ei saa olla tyhjä."}

    tasks = _load_tasks(project_path)
    task = {
        "id": uuid.uuid4().hex[:12],
        "title": (title or clean_prompt[:80]).strip(),
        "prompt": clean_prompt,
        "status": "queued",
        "priority": int(priority),
        "tags": tags or [],
        "created_at": _now(),
        "updated_at": _now(),
        "started_at": None,
        "finished_at": None,
        "last_result": None,
        "error": None,
        "run_count": 0,
    }
    tasks.append(task)
    _save_tasks(project_path, tasks)
    _append_history(project_path, {"event": "task_added", "task_id": task["id"], "title": task["title"], "prompt": task["prompt"]})
    return {"ok": True, "message": "Tehtävä lisätty jonoon.", "task": task, "count": len(tasks)}


def list_tasks(project_path: Path, status: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    tasks = _load_tasks(project_path)
    if status:
        status = status.strip().lower()
        tasks = [task for task in tasks if task.get("status") == status]
    tasks = sorted(
        tasks,
        key=lambda task: (
            {"running": 0, "queued": 1, "failed": 2, "done": 3, "cancelled": 4}.get(task.get("status"), 9),
            -int(task.get("priority", 3)),
            task.get("created_at", ""),
        ),
    )
    tasks = tasks[:max(1, min(int(limit), 500))]
    return {"ok": True, "count": len(tasks), "status": status, "tasks": tasks}


def get_task_queue_status(project_path: Path) -> Dict[str, Any]:
    tasks = _load_tasks(project_path)
    counts = {status: 0 for status in sorted(VALID_STATUSES)}
    for task in tasks:
        status = task.get("status", "queued")
        counts[status] = counts.get(status, 0) + 1
    return {
        "ok": True,
        "message": "Tehtäväjono on käytettävissä.",
        "tasks_path": str(_tasks_path(project_path)),
        "history_path": str(_history_path(project_path)),
        "total": len(tasks),
        "counts": counts,
    }


def _find_task(tasks: List[Dict[str, Any]], task_id: str) -> Optional[Dict[str, Any]]:
    for task in tasks:
        if task.get("id") == task_id:
            return task
    return None


def cancel_task(project_path: Path, task_id: str) -> Dict[str, Any]:
    tasks = _load_tasks(project_path)
    task = _find_task(tasks, task_id)
    if not task:
        return {"ok": False, "message": "Tehtävää ei löytynyt.", "task_id": task_id}
    if task.get("status") in {"done", "failed"}:
        return {"ok": False, "message": f"Tehtävää ei voi perua, koska sen tila on {task.get('status')}.", "task": task}

    task["status"] = "cancelled"
    task["updated_at"] = _now()
    task["finished_at"] = _now()
    _save_tasks(project_path, tasks)
    _append_history(project_path, {"event": "task_cancelled", "task_id": task_id, "title": task.get("title")})
    return {"ok": True, "message": "Tehtävä peruttu.", "task": task}


def _select_next_task(tasks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    queued = [task for task in tasks if task.get("status") == "queued"]
    if not queued:
        return None
    return sorted(queued, key=lambda task: (-int(task.get("priority", 3)), task.get("created_at", "")))[0]


def run_task_by_id(project_path: Path, task_id: str, executor: Callable[[str], Dict[str, Any]]) -> Dict[str, Any]:
    tasks = _load_tasks(project_path)
    task = _find_task(tasks, task_id)
    if not task:
        return {"ok": False, "message": "Tehtävää ei löytynyt.", "task_id": task_id}
    return _run_task(project_path, tasks, task, executor)


def run_next_task(project_path: Path, executor: Callable[[str], Dict[str, Any]]) -> Dict[str, Any]:
    tasks = _load_tasks(project_path)
    task = _select_next_task(tasks)
    if not task:
        return {"ok": True, "message": "Jonossa ei ole suoritettavia tehtäviä.", "task": None}
    return _run_task(project_path, tasks, task, executor)


def _run_task(project_path: Path, tasks: List[Dict[str, Any]], task: Dict[str, Any], executor: Callable[[str], Dict[str, Any]]) -> Dict[str, Any]:
    if task.get("status") not in {"queued", "failed"}:
        return {"ok": False, "message": f"Tehtävää ei voi suorittaa tilassa: {task.get('status')}.", "task": task}

    task["status"] = "running"
    task["started_at"] = _now()
    task["updated_at"] = _now()
    task["run_count"] = int(task.get("run_count", 0)) + 1
    task["error"] = None
    _save_tasks(project_path, tasks)
    _append_history(project_path, {"event": "task_started", "task_id": task.get("id"), "title": task.get("title"), "prompt": task.get("prompt")})

    try:
        result = executor(task.get("prompt", ""))
        ok = bool(result.get("ok", True))
        task["status"] = "done" if ok else "failed"
        task["finished_at"] = _now()
        task["updated_at"] = _now()
        task["last_result"] = _preview(result)
        if not ok:
            task["error"] = result.get("error") or result.get("message") or "Tehtävän suoritus epäonnistui."
        _save_tasks(project_path, tasks)
        _append_history(project_path, {"event": "task_finished" if ok else "task_failed", "task_id": task.get("id"), "title": task.get("title"), "ok": ok, "result": _preview(result)})
        return {"ok": ok, "message": "Tehtävä suoritettu." if ok else "Tehtävän suoritus epäonnistui.", "task": task, "result": result}
    except Exception as error:
        task["status"] = "failed"
        task["finished_at"] = _now()
        task["updated_at"] = _now()
        task["error"] = str(error)
        task["last_result"] = None
        _save_tasks(project_path, tasks)
        _append_history(project_path, {"event": "task_failed", "task_id": task.get("id"), "title": task.get("title"), "error": str(error)})
        return {"ok": False, "message": "Tehtävän suoritus epäonnistui.", "task": task, "error": str(error)}


def read_task_history(project_path: Path, limit: int = 50) -> Dict[str, Any]:
    path = _history_path(project_path)
    if not path.exists():
        return {"ok": True, "count": 0, "items": [], "path": str(path)}
    lines = path.read_text(encoding="utf-8").splitlines()
    selected = lines[-max(1, min(int(limit), 500)):]
    items: List[Dict[str, Any]] = []
    for line in selected:
        try:
            items.append(json.loads(line))
        except Exception:
            items.append({"event": "parse_error", "raw": line})
    return {"ok": True, "count": len(items), "items": items, "path": str(path)}
