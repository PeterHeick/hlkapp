; KlinikPortal — Inno Setup 6 installer-script
; Installerer til %LOCALAPPDATA%\Programs\KlinikPortal\ (ingen UAC)

#define AppName "KlinikPortal"
#define AppVersion "0.2.5"
#define AppPublisher "Hellerup Laserklinik"
#define AppExeName "KlinikPortal.exe"
#define AppSourceDir "dist\KlinikPortal"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={localappdata}\Programs\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=installer
OutputBaseFilename={#AppName}-{#AppVersion}-setup
Compression=lzma2/ultra
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\{#AppExeName}
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "danish"; MessagesFile: "compiler:Languages\Danish.isl"

[Tasks]
Name: "desktopicon"; Description: "Opret genvej på skrivebordet"; GroupDescription: "Genveje:"; Flags: unchecked

[Files]
Source: "{#AppSourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
Name: "{app}\data"
Name: "{app}\data\exports"

[Icons]
Name: "{userprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"
Name: "{userdesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Start {#AppName}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
Filename: "taskkill.exe"; Parameters: "/F /IM {#AppExeName}"; Flags: runhidden; RunOnceId: "KillApp"

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    if DirExists(ExpandConstant('{app}\data')) then
    begin
      if MsgBox('Vil du slette data-mappen (klinik.db, config.json, exports)?',
                mbConfirmation, MB_YESNO) = IDYES then
        DelTree(ExpandConstant('{app}\data'), True, True, True);
    end;
  end;
end;
