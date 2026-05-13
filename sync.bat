@echo off
chcp 65001 >nul
echo ===================================================
echo 🔄 DANG DONG BO MA NGUON LEN GITHUB...
echo ===================================================

:: 1. Kiem tra xem co thay doi nao khong
for /f "delims=" %%a in ('git status --porcelain') do set "CHANGES=%%a"
if "%CHANGES%"=="" (
    echo ⚡ Khong co thay doi nao moi de commit!
    goto :pull_and_push
)

:: 2. Them thay doi va commit
git add .
set /p commit_msg="📝 Nhap noi dung commit (Enter de dung 'Auto sync'): "
if "%commit_msg%"=="" set commit_msg=Auto sync
git commit -m "%commit_msg%"

:pull_and_push
:: 3. Cap nhat code moi nhat ve truoc (tranh conflict)
echo.
echo 📥 Dang cap nhat code tu GitHub...
git pull origin main --rebase
if %errorlevel% neq 0 (
    echo ❌ LOI: Khong the pull code. Vui long xu ly conflict!
    goto :end
)

:: 4. Day code len
echo.
echo 📤 Dang day code len GitHub...
git push origin main
if %errorlevel% neq 0 (
    echo ❌ LOI: Khong the day code len GitHub. Kiem tra lai ket noi hoac quyen truy cap!
    goto :end
)

echo.
echo ✅ DONG BO THANH CONG CHINH XAC 100%%!

:end
echo ===================================================
pause