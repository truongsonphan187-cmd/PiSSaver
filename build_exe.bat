@echo off
echo ===================================================
echo [PiSSaver] Dang dong goi ung dung ra file .exe...
echo ===================================================

python -m PyInstaller --clean --noconsole --onefile ^
    --icon "assets/icon.ico" ^
    --name "PiSSaver" ^
    --add-data "assets;assets" ^
    --add-data "src/shaders;shaders" ^
    --add-data "src/shaders;src/shaders" ^
    --hidden-import "PyQt6" ^
    --hidden-import "PyQt6.QtCore" ^
    --hidden-import "PyQt6.QtGui" ^
    --hidden-import "PyQt6.QtWidgets" ^
    --hidden-import "PyQt6.QtOpenGL" ^
    --hidden-import "PyQt6.QtOpenGLWidgets" ^
    --hidden-import "OpenGL" ^
    --hidden-import "OpenGL.GL" ^
    --hidden-import "OpenGL.platform" ^
    --hidden-import "OpenGL.platform.win32" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL.Image" ^
    --hidden-import "numpy" ^
    src/main.py

echo.
echo ===================================================
echo [PiSSaver] Hoan tat! File chay: dist\PiSSaver.exe
echo ===================================================
pause
