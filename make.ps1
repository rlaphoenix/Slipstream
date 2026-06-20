function Confirm-Step([string]$Message, [string]$Suffix, [bool]$DefaultYes) {
    $answer = (Read-Host "$Message $Suffix").Trim().ToLower()
    if ($answer -eq '') { return $DefaultYes }
    return $answer -in @('y', 'yes')
}

if (Confirm-Step 'Recompile GUI from UI file?' '(y/N)' $false) {
    pyside6-uic pslipstream/gui/main_window.ui -o pslipstream/gui/main_window_ui.py
    $code = $LASTEXITCODE
    if ($code -ne 0) {
        Write-Error "pyside6-uic failed to compile the UI file (exit code $code)."
        exit $code
    }
    ruff check pslipstream/gui/main_window_ui.py --fix
    # ignore type checks in the uic file
    $filePath = 'pslipstream/gui/main_window_ui.py'
    "# pylint: disable-all`n# type: ignore`n$((Get-Content -Path $filePath) -join [System.Environment]::NewLine)" | Set-Content -Path $filePath
}

if (Confirm-Step 'Build to a self-contained folder via PyInstaller?' '(Y/n)' $true) {
    & 'uv' run --group pack python -OO pyinstaller.py
    $code = $LASTEXITCODE
    if ($code -ne 0) {
        Write-Error "PyInstaller build failed (exit code $code)."
        exit $code
    }
    Write-Output 'Done! /dist contains the PyInstaller build.'
    if (Confirm-Step 'Execute the frozen build''s executable?' '(Y/n)' $true) {
        & 'dist/Slipstream/Slipstream.exe' ($args | Select-Object -Skip 1)
        exit
    }
}

if (Confirm-Step 'Create a Windows installer via Inno Setup?' '(Y/n)' $true) {
    & 'iscc' setup.iss
    $code = $LASTEXITCODE
    if ($code -ne 0) {
        Write-Error "Inno Setup build failed (exit code $code)."
        exit $code
    }
    Write-Output 'Done! /dist contains the Inno Setup installer.'
}
