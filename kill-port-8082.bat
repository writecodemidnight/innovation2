@echo off
chcp 65001 >nul
echo 正在查找占用 8082 端口的进程...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8082.*LISTENING"') do (
    echo 发现进程 PID: %%a
    taskkill /PID %%a /F 2>nul
    if errorlevel 1 (
        echo 无法终止进程，可能需要管理员权限
    ) else (
        echo 已终止进程 %%a
    )
)

echo.
echo 端口 8082 已清理
pause
