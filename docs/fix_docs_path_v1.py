from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import re
import shutil


PROJECT_ROOT_CODE = 'PROJECT_ROOT = Path(__file__).resolve().parent.parent\n'


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def backup_file(path: Path) -> Path:
    backup = path.with_name(f"{path.stem}_backup_docs_path_v1_{timestamp()}{path.suffix}")
    shutil.copy2(path, backup)
    return backup


def ensure_project_root_definition(text: str) -> str:
    """
    Lisää PROJECT_ROOT-määrityksen imports-osan jälkeen, jos sitä ei vielä ole.
    PROJECT_ROOT osoittaa projektin juureen:
    C:\\Sade\\Sade-v1
    kun tiedosto sijaitsee app-kansiossa.
    """
    if "PROJECT_ROOT = Path(__file__).resolve().parent.parent" in text:
        return text

    if "from pathlib import Path" not in text:
        text = "from pathlib import Path\n" + text

    marker = "from pathlib import Path\n"
    return text.replace(marker, marker + "\n" + PROJECT_ROOT_CODE, 1)


def replace_project_root_patterns(text: str) -> str:
    """
    Korvaa yleisimmät epävarmat projektijuurimääritykset.
    """
    replacements = {
        "PROJECT_ROOT = Path.cwd()": "PROJECT_ROOT = Path(__file__).resolve().parent.parent",
        "PROJECT_ROOT = Path('.')": "PROJECT_ROOT = Path(__file__).resolve().parent.parent",
        'PROJECT_ROOT = Path(".")': "PROJECT_ROOT = Path(__file__).resolve().parent.parent",

        "BASE_PATH = Path.cwd()": "BASE_PATH = PROJECT_ROOT",
        "BASE_PATH = Path('.')": "BASE_PATH = PROJECT_ROOT",
        'BASE_PATH = Path(".")': "BASE_PATH = PROJECT_ROOT",

        "BASE_DIR = Path.cwd()": "BASE_DIR = PROJECT_ROOT",
        "BASE_DIR = Path('.')": "BASE_DIR = PROJECT_ROOT",
        'BASE_DIR = Path(".")': "BASE_DIR = PROJECT_ROOT",

        "ROOT_PATH = Path.cwd()": "ROOT_PATH = PROJECT_ROOT",
        "ROOT_PATH = Path('.')": "ROOT_PATH = PROJECT_ROOT",
        'ROOT_PATH = Path(".")': "ROOT_PATH = PROJECT_ROOT",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def add_docs_to_allowed_dirs(text: str) -> str:
    """
    Lisää docs sallittuihin kansioihin, jos tiedostossa on ALLOWED_DIRS /
    SAFE_DIRS / ALLOWED_ROOTS -tyyppinen lista.
    """
    if '"docs"' in text or "'docs'" in text:
        return text

    patterns = [
        r"(ALLOWED_DIRS\s*=\s*\[)([^\]]*)(\])",
        r"(SAFE_DIRS\s*=\s*\[)([^\]]*)(\])",
        r"(ALLOWED_ROOTS\s*=\s*\[)([^\]]*)(\])",
        r"(ALLOWED_FOLDERS\s*=\s*\[)([^\]]*)(\])",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.DOTALL)
        if not match:
            continue

        start, body, end = match.groups()

        if "memory" in body or "uploads" in body:
            new_body = body.rstrip()
            if new_body and not new_body.rstrip().endswith(","):
                new_body += ","
            new_body += '\n    "docs",\n'
            return text[:match.start()] + start + new_body + end + text[match.end():]

    return text


def patch_path_resolution(text: str) -> str:
    """
    Korjaa yleisiä tapoja muodostaa tiedostopolku niin,
    että suhteelliset polut luetaan PROJECT_ROOTin alta.
    """
    replacements = {
        "file_path = Path(path)": "file_path = (PROJECT_ROOT / path).resolve()",
        "target_path = Path(path)": "target_path = (PROJECT_ROOT / path).resolve()",
        "full_path = Path(path)": "full_path = (PROJECT_ROOT / path).resolve()",

        "file_path = BASE_PATH / path": "file_path = (PROJECT_ROOT / path).resolve()",
        "target_path = BASE_PATH / path": "target_path = (PROJECT_ROOT / path).resolve()",
        "full_path = BASE_PATH / path": "full_path = (PROJECT_ROOT / path).resolve()",

        "file_path = BASE_DIR / path": "file_path = (PROJECT_ROOT / path).resolve()",
        "target_path = BASE_DIR / path": "target_path = (PROJECT_ROOT / path).resolve()",
        "full_path = BASE_DIR / path": "full_path = (PROJECT_ROOT / path).resolve()",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def add_safe_resolve_helper(text: str) -> str:
    """
    Lisää turvallinen resolve_project_path-apufunktio, jos sitä ei ole.
    Tätä voi käyttää myöhemmin tools.py:ssä ja tool_router.py:ssä.
    """
    if "def resolve_project_path(" in text:
        return text

    helper = r'''


def resolve_project_path(relative_path: str) -> Path:
    """
    Palauttaa turvallisen polun projektin juuren sisältä.

    Esimerkki:
    docs/project_inventory.md
    -> C:\Sade\Sade-v1\docs\project_inventory.md

    Estää polut, jotka yrittävät karata projektikansion ulkopuolelle.
    """
    candidate = (PROJECT_ROOT / relative_path).resolve()

    try:
        candidate.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise ValueError(f"Polku ei saa olla projektikansion ulkopuolella: {relative_path}") from exc

    return candidate

'''
    return text + helper


def patch_file(path: Path) -> bool:
    if not path.exists():
        print(f"Ohitetaan, tiedostoa ei löydy: {path}")
        return False

    original = path.read_text(encoding="utf-8")
    text = original

    text = ensure_project_root_definition(text)
    text = replace_project_root_patterns(text)
    text = add_docs_to_allowed_dirs(text)
    text = patch_path_resolution(text)
    text = add_safe_resolve_helper(text)

    if text == original:
        print(f"Ei muutoksia tiedostoon: {path}")
        return False

    backup = backup_file(path)
    print(f"Varmuuskopioitu: {backup}")

    compile(text, str(path), "exec")

    path.write_text(text, encoding="utf-8")
    py_compile.compile(str(path), doraise=True)

    print(f"Päivitetty ja syntaksitarkistettu: {path}")
    return True


def main() -> None:
    project_root = Path.cwd().resolve()

    if not (project_root / "app").exists():
        raise RuntimeError(
            "Aja tämä projektin juuresta:\n"
            "cd C:\\Sade\\Sade-v1\n"
            "python fix_docs_path_v1.py"
        )

    docs_file = project_root / "docs" / "project_inventory.md"
    if not docs_file.exists():
        print("VAROITUS: docs/project_inventory.md ei löytynyt.")
        print("Tarkista, että tiedosto on oikeassa paikassa.")
    else:
        print(f"Löytyi: {docs_file}")

    targets = [
        project_root / "app" / "tools.py",
        project_root / "app" / "tool_router.py",
    ]

    changed = False
    for target in targets:
        changed = patch_file(target) or changed

    print()
    if changed:
        print("Valmis: docs-polun lukukorjaus tehty.")
        print()
        print("Käynnistä Säde v1 uudelleen:")
        print("python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8008")
        print()
        print("Testaa paikallisessa Säteessä:")
        print("lue tiedosto docs/project_inventory.md")
        print("indeksoi tiedosto docs/project_inventory.md")
        print("hae muistista project inventory")
    else:
        print("Skripti ei tehnyt muutoksia.")
        print("Silloin tools.py käyttää todennäköisesti erilaista rakennetta.")
        print("Lähetä app/tools.py tänne, niin teen tarkan korjauksen siihen.")


if __name__ == "__main__":
    main()
