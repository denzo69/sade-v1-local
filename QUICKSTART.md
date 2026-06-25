# Quickstart — Local AI Workspace

## 1. Siirry projektikansioon

```powershell
cd C:\Sade\Sade-v1
```

## 2. Luo virtuaaliympäristö tarvittaessa

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 3. Luo kirjautumiskäyttäjä

```powershell
.\app\create_sade_user.bat
```

## 4. Käynnistä

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8080
```

## 5. Avaa käyttöliittymä

```text
http://127.0.0.1:8080/ui
```

## 6. Aja testit

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```
