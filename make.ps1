$runUic = Read-Host 'Recompile GUI from UI file? (y/n) [y]'
if ($runUic -eq 'y') {
    pyside6-uic pslipstream/gui/main_window.ui -o pslipstream/gui/main_window_ui.py
    ruff check pslipstream/gui/main_window_ui.py --fix
    isort pslipstream/gui/main_window_ui.py
    # ignore type checks in the uic file
    $filePath = 'pslipstream/gui/main_window_ui.py'
    "# pylint: disable-all`n# type: ignore`n$((Get-Content -Path $filePath) -join [System.Environment]::NewLine)" | Set-Content -Path $filePath
}

$runPyInstaller = Read-Host 'Build to a self-contained folder via PyInstaller? (Y/n)'
if ($runPyInstaller -eq 'y') {
    & 'poetry' run python -OO pyinstaller.py
    Write-Output 'Done! /dist contains the PyInstaller build.'
    $executePyInstaller = Read-Host 'Execute the frozen build''s executable? (Y/n)'
    if ($executePyInstaller -eq 'y') {
        & 'dist/Slipstream/Slipstream.exe' ($args | Select-Object -Skip 1)
        exit
    }
}

$runInnoSetup = Read-Host 'Create a Windows installer via Inno Setup? (Y/n)'
if ($runInnoSetup -eq 'y') {
    & 'iscc' setup.iss
    Write-Output 'Done! /dist contains the Inno Setup installer.'
}
