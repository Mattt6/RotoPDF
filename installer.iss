[Setup]
AppName=RotoPDF
AppVersion=1.0
AppPublisher=Mattt6
AppCopyright=Copyright (C) 2026 Mattt6
DefaultDirName={autopf}\RotoPDF
DefaultGroupName=RotoPDF
OutputBaseFilename=RotoPDF_Setup
OutputDir=Output
SetupIconFile=icon.ico
UninstallDisplayIcon={app}\RotoPDF.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "Créer un raccourci sur le Bureau"; GroupDescription: "Raccourcis :"

[Files]
Source: "dist\RotoPDF\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion
Source: "LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "THIRD_PARTY_NOTICES.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\RotoPDF"; Filename: "{app}\RotoPDF.exe"
Name: "{autodesktop}\RotoPDF"; Filename: "{app}\RotoPDF.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\RotoPDF.exe"; Description: "Lancer RotoPDF"; Flags: nowait postinstall skipifsilent
