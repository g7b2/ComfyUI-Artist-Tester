@echo off
echo ==========================================
echo       Start Uploading to GitHub...
echo ==========================================

:: 1. 添加所有文件
git add .

:: 2. 自动提交（你可以改下面的备注）
git commit -m "Auto update by script"

:: 3. 推送
git push origin main

echo ==========================================
echo             Upload Success!
echo ==========================================
pause