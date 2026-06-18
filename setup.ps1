# ============================================================
# Script setup cho project AI Agent trong Khoa hoc May tinh
# Cai dat dependencies va chuan bi moi truong
# ============================================================

Write-Host "=== Cai dat dependencies cho AI Agent CS Project ===" -ForegroundColor Cyan

# Kiem tra Python
try {
    $pyVer = python --version
    Write-Host "Python: $pyVer" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Can cai dat Python >= 3.9" -ForegroundColor Red
    exit 1
}

# Cai dat packages
Write-Host "`n>>> Cai dat packages..." -ForegroundColor Yellow
pip install -r requirements.txt

# Kiem tra thanh cong
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n=== Cai dat hoan tat thanh cong! ===" -ForegroundColor Green
    Write-Host "Chay app: streamlit run app.py" -ForegroundColor Cyan
} else {
    Write-Host "ERROR: Cai dat that bai!" -ForegroundColor Red
}

Write-Host "`n=== Huong dan push len GitHub ===" -ForegroundColor Cyan
Write-Host @"
git init
git add .
git commit -m "Initial commit: AI Agent CS Analysis"
git branch -M main
git remote add origin https://github.com/<USERNAME>/<REPO>.git
git push -u origin main
"@
