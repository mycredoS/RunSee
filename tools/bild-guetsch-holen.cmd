@echo off
rem Top-Views-Bild auf den Blick vom Guetsch umstellen
setlocal
set "ORIG=%~dp0..\assets\images\_originals"
set "RES=%ORIG%\_reserve"
set "UA=RunAndSeeLucerne-SiteBuild/1.0 (philippe@runandsee.ch)"
if not exist "%RES%" mkdir "%RES%"
if exist "%ORIG%\tour-top-views.jpg" move /Y "%ORIG%\tour-top-views.jpg" "%RES%\tour-top-views-museggmauer.jpg" >nul
echo Lade Blick vom Guetsch ...
curl -sS -L -A "%UA%" -o "%ORIG%\tour-top-views.jpg" "https://commons.wikimedia.org/wiki/Special:FilePath/Luzern_asv2022-10_Blick_vom_G%%C3%%BCtsch_img1.jpg?width=3840"
if errorlevel 1 (echo FEHLER - Download fehlgeschlagen) else (echo OK)
echo.
dir "%ORIG%\tour-top-views.jpg"
echo.
echo Die Museggmauer liegt jetzt als Reserve in _originals\_reserve
echo.
pause
