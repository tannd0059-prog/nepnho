@echo off
chcp 65001 >nul
title ĐẨY CODE LÊN GITHUB ĐỂ ĐƯA LÊN RENDER
color 0A
echo ====================================================================
echo 🚀 HƯỚNG DẪN ĐẨY CODE LÊN GITHUB ĐỂ ĐƯA LÊN RENDER CHẠY 24/7
echo ====================================================================
echo.
echo Bước 1: Bạn vào https://github.com/new và tạo 1 repository mới
echo         (Ví dụ đặt tên là: nepnho-d2c)
echo.
echo Bước 2: Dán đường link git repository của bạn vào bên dưới:
echo         (Ví dụ: https://github.com/tannd0059-prog/nepnho-d2c.git)
echo.
set /p REPO_URL="https://github.com/tannd0059-prog/nepnho.git "

if "%REPO_URL%"=="" (
    echo [X] Bạn chưa nhập link GitHub! Vui lòng chạy lại.
    pause
    exit /b
)

git remote remove origin 2>nul
git remote add origin %REPO_URL%
git branch -M main
echo.
echo Đang đồng bộ và đẩy mã nguồn lên GitHub...
git push -u origin main

echo.
echo ====================================================================
echo ✓ ĐÃ ĐẨY LÊN GITHUB THÀNH CÔNG!
echo Bây giờ bạn chỉ cần vào https://dashboard.render.com -> New Web Service
echo và chọn repository này là xong!
echo ====================================================================
pause
