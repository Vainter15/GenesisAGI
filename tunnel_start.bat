@echo off
title Защитный Туннель Genesis
color 0A

:loop
echo [ %time% ] Запуск туннеля...
REM --- ВСТАВЬ НИЖЕ СВОЮ КОМАНДУ ТУННЕЛЯ ---
ssh -D 1080 -N vpn@91.211.15.93 -o ServerAliveInterval=30 -o ServerAliveCountMax=3

echo [ %time% ] ВНИМАНИЕ: Туннель упал! Перезапуск через 3 секунды...
timeout /t 3 >nul
goto loop