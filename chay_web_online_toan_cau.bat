@echo off
chcp 65001 > nul
title Nếp Nhỏ D2C - Chạy Web Online Toàn Cầu
cd /d "%~dp0"
echo ================================================================
echo 🚀 ĐANG MỞ MẠNG PUBLIC CHO NẾP NHỎ D2C...
echo ================================================================
python run_public.py
pause
