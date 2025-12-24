@echo off
REM Booker Build Script
REM Builds the application into a standalone Windows executable

echo ========================================
echo    Building Booker Desktop App
echo ========================================
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller>=6.0.0
)

REM Clean previous builds
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM Build the application
echo Building executable...
pyinstaller booker.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo Build failed! Please check the errors above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo    Build Complete!
echo ========================================
echo.
echo Your application is ready at:
echo    dist\Booker\Booker.exe
echo.
echo You can now:
echo  1. Run Booker.exe directly from dist\Booker\
echo  2. Zip the dist\Booker folder for distribution
echo  3. Create an installer using NSIS or Inno Setup
echo.
pause
