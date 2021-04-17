; https://jrsoftware.org/ishelp/index.php

#define AppName "Slipstream"
#define Version "0.4.0"
#define AppExeName "Slipstream.exe"

[Setup]
AppId={{88EAF5E9-A032-4322-95C9-89FB13E38278}
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
; Uncomment the following line to run in non administrative install mode (install for current user only.)
;PrivilegesRequired=lowest
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\phoenix\Git\Slipstream\dist\Slipstream\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\phoenix\Git\Slipstream\dist\Slipstream\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

