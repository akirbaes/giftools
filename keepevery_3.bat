setlocal enabledelayedexpansion
echo %~n0
mkdir aside
set counter=0
REM 
@echo off
FOR /f "tokens=2 delims=_" %%d in ("%~n0") DO (
    echo Result: %%d
    set divider=%%d
    )
REM @echo on
FOR %%i IN (*.png) DO (
    REM echo Counter: !counter!
    if !counter! neq 0 (
    move %%i aside\\%%i
    )
    if !counter! equ 0 (
    echo Keep: "%%i"
    )
    set /a counter+=1
    if !counter! equ !divider! (
    REM echo Wrap around
    set /a counter=0
    )
)

set /p DUMMY=Hit ENTER to continue... 