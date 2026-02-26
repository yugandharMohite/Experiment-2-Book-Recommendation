# PowerShell script to run the end-to-end Book Recommendation Pipeline

Write-Host "--- Starting Book Recommendation Pipeline ---" -ForegroundColor Cyan

# 1. Preprocess
Write-Host "[1/4] Preprocessing data..." -ForegroundColor Yellow
Set-Location src
python preprocess.py
Set-Location ..

# 2. Train
Write-Host "[2/4] Training model..." -ForegroundColor Yellow
Set-Location src
python train.py
Set-Location ..

# 3. Start API
Write-Host "[3/4] Starting FastAPI in background..." -ForegroundColor Yellow
Start-Process -NoNewWindow python -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 5

# 4. Start Dashboard
Write-Host "[4/4] Starting Streamlit dashboard..." -ForegroundColor Yellow
streamlit run app/dashboard.py --server.port 8501
