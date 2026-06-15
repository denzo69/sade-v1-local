# Säde v1 - semanttisen muistin riippuvuudet
# Aja projektikansiossa:
#   cd C:\Sade\Sade-v1
#   powershell -ExecutionPolicy Bypass -File C:\Sade\install_semantic_memory.ps1

Write-Host "Asennetaan semanttisen muistin riippuvuudet..." -ForegroundColor Yellow

python -m pip install --upgrade pip
python -m pip install chromadb sentence-transformers

Write-Host ""
Write-Host "Valmis. Käynnistä palvelin uudelleen:" -ForegroundColor Green
Write-Host "cd C:\Sade\Sade-v1"
Write-Host "python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8008"
Write-Host ""
Write-Host "Kun palvelin on käynnissä, indeksoi muisti avaamalla:"
Write-Host "http://127.0.0.1:8008/docs"
Write-Host "ja aja POST /memory/semantic/rebuild"
