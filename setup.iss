; https://jrsoftware.org/ishelp/index.php

#define AppName "Slipstream"

; Read [project].version from pyproject.toml (the single source of truth) at compile time, so the
; installer version never has to be passed in or kept in sync by hand.
#define Q """"
#define Version ""
#define PyProject FileOpen("pyproject.toml")
#if !PyProject
  #error Could not open pyproject.toml to read the version
#endif

#sub ReadVersionLine
  #expr Local[0] = FileRead(PyProject), \
    (Len(Version) == 0) && (Pos("version", Local[0]) == 1) && (Pos(Q, Local[0]) > 0) ? \
      (Local[1] = Copy(Local[0], Pos(Q, Local[0]) + 1, Len(Local[0])), \
       Version = Copy(Local[1], 1, Pos(Q, Local[1]) - 1)) : 0
#endsub

#for {0; !FileEof(PyProject); 0} ReadVersionLine
#expr FileClose(PyProject)

#if Len(Version) == 0
  #error Could not find [project].version in pyproject.toml
#endif

[Setup]
AppId={#AppName}
AppName={#AppName}
AppPublisher=rlaphoenix
AppPublisherURL=https://github.com/Homemediadb/Slipstream
AppReadmeFile=https://github.com/Homemediadb/Slipstream/blob/master/README.md
AppSupportURL=https://github.com/Homemediadb/Slipstream/discussions
AppUpdatesURL=https://github.com/Homemediadb/Slipstream/releases
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
VersionInfoVersion={#Version}
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
