Write-Output 'Building to self-contained folder via PyInstaller'
& 'poetry' run python -OO pyinstaller.py

if ($args[0] -eq 'run') {
    & 'dist/Slipstream/Slipstream.exe' ($args | Select-Object -Skip 1)
    exit
}

Write-Output 'Creating Windows installer via Inno Setup'
& 'iscc' setup.iss

Write-Output 'Done! /dist contains the pyinstaller build and the Inno Setup installer.'
