echo Building to self-contained folder via PyInstaller
call poetry run python pyinstaller.py
echo Creating Windows installer via Inno Setup
call iscc setup.iss

echo Done! /dist contains the pyinstaller build and the Inno Setup installer.
