[Setup]
AppName=Kestrel
AppVersion=1.0
DefaultDirName={autopf}\Kestrel
DefaultGroupName=Kestrel
UninstallDisplayIcon={app}\Kestrel.exe
SetupIconFile=Kestrel.ico
Compression=lzma2
SolidCompression=yes
OutputDir=user_installer
OutputBaseFilename=Kestrel_Setup

[Files]
Source: "dist\Kestrel\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs
Source: "Kestrel.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Kestrel"; Filename: "{app}\Kestrel.exe"; IconFilename: "{app}\Kestrel.ico"
Name: "{commondesktop}\Kestrel"; Filename: "{app}\Kestrel.exe"; IconFilename: "{app}\Kestrel.ico"


[Run]
Filename: "{app}\Kestrel.exe"; Description: "Lanzar Kestrel"; Flags: nowait postinstall skipifsilent

[Registry]
; Opcional: Registrar como gestor de carpetas (esto requiere cuidado, lo manejaremos mejor con un script aparte o botón en la app)
; Root: HKCR; Subkey: "Directory\shell\Kestrel"; ValueType: string; ValueName: ""; ValueData: "Abrir con Kestrel"; Flags: uninsdeletekey
; Root: HKCR; Subkey: "Directory\shell\Kestrel\command"; ValueType: string; ValueName: ""; ValueData: """{app}\Kestrel.exe"" ""%1"""; Flags: uninsdeletekey
