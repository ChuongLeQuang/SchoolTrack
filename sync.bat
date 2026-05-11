@echo off
chcp 65001 >nul
echo 🔄 Dang dong bo ma nguon len GitHub...
git add .
set /p commit_msg="Nhap noi dung commit: "
if "%commit_msg%"=="" set commit_msg="Auto sync"
git commit -m "%commit_msg%"
git push origin main
echo ✅ Dong bo thanh cong!
pause