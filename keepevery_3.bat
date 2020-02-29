setlocal enabledelayedexpansion
REM echo %~n0
mkdir aside
set counter=0
@echo off
REM Take the part after _ in the script filename as number
FOR /f "tokens=2 delims=_" %%d in ("%~n0") DO (
    echo Will take every %%d frame
    set divider=%%d
    )
REM Only go over PNG files
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
        REM Wrap back
        set /a counter=0
    )
)

set /p DUMMY=Hit ENTER to continue... 