@echo off
chcp 65001 >nul
title SXJ 网站一键推送工具

echo ============================================
echo   SXJ 网站一键推送工具
echo   推送到 GitHub 后自动部署到 GitHub Pages
echo ============================================
echo.

REM 检查是否有改动
git diff --exit-code --quiet
git diff --cached --exit-code --quiet
if %errorlevel%==0 (
    echo [提示] 没有检测到文件改动。
    set /p confirm="是否仍要强制推送？(y/n): "
    if /i not "%confirm%"=="y" goto :eof
)

echo [1/3] 添加所有改动...
git add -A

echo [2/3] 提交改动...
set /p msg="请输入提交说明（直接回车用默认）: "
if "%msg%"=="" set msg=Update %date% %time%
git commit -m "%msg%"

echo [3/3] 推送到 GitHub...
git push origin main

if %errorlevel%==0 (
    echo.
    echo ============================================
    echo   推送成功！
    echo   GitHub Actions 正在自动部署...
    echo   约 1-2 分钟后网站将更新
    echo   访问 https://github.com/你的用户名/sxj-international/actions
    echo   查看部署进度
    echo ============================================
) else (
    echo.
    echo [错误] 推送失败，请检查网络或认证信息
)

pause
