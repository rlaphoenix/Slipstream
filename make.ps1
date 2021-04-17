Write-Output 'Building to self-contained folder via PyInstaller'
& 'poetry' run python pyinstaller.py
Write-Output 'Creating Windows installer via Inno Setup'
& 'iscc' setup.iss

Write-Output 'Done! /dist contains the pyinstaller build and the Inno Setup installer.'
