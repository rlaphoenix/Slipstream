; https://jrsoftware.org/ishelp/index.php

#define AppName "Slipstream"
#define Version "0.4.0"

[Setup]
AppId={#AppName}
AppName={#AppName}
AppPublisher=PHOENiX
AppPublisherURL=https://github.com/rlaphoenix/slipstream
AppReadmeFile=https://github.com/rlaPHOENiX/Slipstream/blob/master/README.md
AppSupportURL=https://github.com/rlaPHOENiX/Slipstream/discussions
AppUpdatesURL=https://github.com/rlaphoenix/slipstream/releases
AppVerName={#AppName} {#Version}
AppVersion={#Version}
ArchitecturesAllowed=x64
Compression=lzma2/max
DefaultDirName={autopf}\{#AppName}
LicenseFile=LICENSE
; Python 3.9 has dropped support for <= Windows 7/Server 2008 R2 SP1. https://jrsoftware.org/ishelp/index.php?topic=winvernotes
MinVersion=6.2
OutputBaseFilename=Slipstream-Setup
OutputDir=dist
OutputManifestFile=Slipstream-Setup-Manifest.txt
PrivilegesRequiredOverridesAllowed=dialog commandline
SetupIconFile=pslipstream/static/img/icon.ico
SolidCompression=yes
VersionInfoVersion=0.1.0
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: dist\Slipstream\{#AppName}.exe; DestDir: {app}; Flags: ignoreversion
Source: dist\Slipstream\*; DestDir: {app}; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppName}.exe"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppName}.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppName}.exe"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
