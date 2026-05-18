[Setup]
AppName=UltraExplorer
AppVersion=1.0
DefaultDirName={autopf}\UltraExplorer
DefaultGroupName=UltraExplorer
UninstallDisplayIcon={app}\UltraExplorer.exe
SetupIconFile=UltraExplorer.ico
Compression=lzma2
SolidCompression=yes
OutputDir=user_installer
OutputBaseFilename=UltraExplorer_Setup

[Files]
Source: "dist\UltraExplorer\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs
Source: "UltraExplorer.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\UltraExplorer"; Filename: "{app}\UltraExplorer.exe"; IconFilename: "{app}\UltraExplorer.ico"
Name: "{commondesktop}\UltraExplorer"; Filename: "{app}\UltraExplorer.exe"; IconFilename: "{app}\UltraExplorer.ico"


[Run]
Filename: "{app}\UltraExplorer.exe"; Description: "Lanzar UltraExplorer"; Flags: nowait postinstall skipifsilent

[Registry]
; Opcional: Registrar como gestor de carpetas (esto requiere cuidado, lo manejaremos mejor con un script aparte o botón en la app)
; Root: HKCR; Subkey: "Directory\shell\UltraExplorer"; ValueType: string; ValueName: ""; ValueData: "Abrir con UltraExplorer"; Flags: uninsdeletekey
; Root: HKCR; Subkey: "Directory\shell\UltraExplorer\command"; ValueType: string; ValueName: ""; ValueData: """{app}\UltraExplorer.exe"" ""%1"""; Flags: uninsdeletekey
