@echo off
rem Bilder von Wikimedia Commons holen - Run ^& See Lucerne
rem Doppelklick genuegt. Nutzt curl.exe, das in Windows 10/11 enthalten ist.
rem Das Fenster bleibt offen, das Protokoll steht in bilder-holen.log

setlocal
set "DEST=%~dp0..\assets\images\_originals"
set "LOG=%~dp0bilder-holen.log"
set "UA=RunAndSeeLucerne-SiteBuild/1.0 (philippe@runandsee.ch)"
set "BASE=https://commons.wikimedia.org/wiki/Special:FilePath"

if not exist "%DEST%" mkdir "%DEST%"
echo Lauf vom %DATE% %TIME% > "%LOG%"
echo Zielordner: %DEST% >> "%LOG%"
where curl >> "%LOG%" 2>&1
echo.>> "%LOG%"

echo Lade luzern-kapellbruecke.jpg ...
curl -sS -L -A "%UA%" -o "%DEST%\luzern-kapellbruecke.jpg" "%BASE%/Luzern_Kapellbruecke.jpg?width=3840" >> "%LOG%" 2>&1
if errorlevel 1 (echo FEHLER luzern-kapellbruecke.jpg>> "%LOG%") else (echo OK     luzern-kapellbruecke.jpg>> "%LOG%")

echo Lade tour-morning-run.jpg ...
curl -sS -L -A "%UA%" -o "%DEST%\tour-morning-run.jpg" "%BASE%/Luzern_Pilatus_and_Lake_1170975.jpg?width=3840" >> "%LOG%" 2>&1
if errorlevel 1 (echo FEHLER tour-morning-run.jpg>> "%LOG%") else (echo OK     tour-morning-run.jpg>> "%LOG%")

echo Lade tour-heritage.jpg ...
curl -sS -L -A "%UA%" -o "%DEST%\tour-heritage.jpg" "%BASE%/L%%C3%%B6wendenkmal_-_The_Lion_Monument_(Lucerne)_02.jpg?width=3840" >> "%LOG%" 2>&1
if errorlevel 1 (echo FEHLER tour-heritage.jpg>> "%LOG%") else (echo OK     tour-heritage.jpg>> "%LOG%")

echo Lade tour-hidden-gems.jpg ...
curl -sS -L -A "%UA%" -o "%DEST%\tour-hidden-gems.jpg" "%BASE%/Alter_Friedhof_Propsteimatte.jpg?width=3840" >> "%LOG%" 2>&1
if errorlevel 1 (echo FEHLER tour-hidden-gems.jpg>> "%LOG%") else (echo OK     tour-hidden-gems.jpg>> "%LOG%")

echo Lade tour-top-views.jpg ...
curl -sS -L -A "%UA%" -o "%DEST%\tour-top-views.jpg" "%BASE%/Luzern_asv2022-10_Blick_von_Museggmauer.jpg?width=3840" >> "%LOG%" 2>&1
if errorlevel 1 (echo FEHLER tour-top-views.jpg>> "%LOG%") else (echo OK     tour-top-views.jpg>> "%LOG%")

echo.>> "%LOG%"
dir "%DEST%" >> "%LOG%" 2>&1

cls
type "%LOG%"
echo.
echo Protokoll: %LOG%
echo.
pause
