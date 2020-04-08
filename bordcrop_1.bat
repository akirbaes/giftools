FOR /f "tokens=2 delims=_" %%d in ("%~n0") DO (
    set border=%%d
    )
    
FOR %%A IN (%*) DO (
python "%~dp0\crop_image.py" --crop %border% %%A
)
pause