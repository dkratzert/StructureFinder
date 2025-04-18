; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "StructureFinder"
;#define MyAppVersion "74"  ; This is now done by commandline argument
#define MyAppPublisher "Daniel Kratzert"

; Remember, first run pyInstaller script!

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{FD3791DD-E642-47A6-8434-FBD976271019}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={commonpf}\{#MyAppName}
OutputBaseFilename={#MyAppName}-setup-x64-v{#MyAppVersion}
Compression=lzma2/fast
SolidCompression=yes
SetupLogging=True
CloseApplications=False
RestartApplications=False
ShowLanguageDialog=no
ChangesAssociations=True
RestartIfNeededByRun=False
ChangesEnvironment=True
DisableFinishedPage=True
DisableReadyPage=True
DisableReadyMemo=True
DisableWelcomePage=True
AlwaysShowDirOnReadyPage=True
InternalCompressLevel=fast
EnableDirDoesntExistWarning=True
DirExistsWarning=no
UninstallLogMode=new
VersionInfoVersion={#MyAppVersion}
MinVersion=10.0.10240
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
AppendDefaultGroupName=True
AppContact=dkratzert@gmx.de
AppCopyright=Daniel Kratzert
AppSupportPhone=+49 761 203 6156
VersionInfoProductName={#MyAppName}
AlwaysShowComponentsList=False
ShowComponentSizes=False
SetupIconFile="..\icons\strf.ico"
UninstallDisplayIcon={app}\{#MyAppName}.exe
SignTool=sign_sha256




[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

; adds a new page to the setup where you can choose if the path should be added
;Excludes: "*.pyc"

[Run]
Filename: "{app}\vc_redist.x64.exe"; WorkingDir: "{app}"; Parameters: "/passive /norestart"

[UninstallRun]

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\structurefinder.exe"; WorkingDir: "{app}"; IconFilename: "{app}\icons\strf.ico"; Check: IsWin64
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"; IconFilename: "{app}\icons\strf.ico"

[UninstallDelete]
Type: files; Name: "{app}\*.pyc"
; too dangerous:
;Type: files; Name: "{app}\*.*"
;Type: filesandordirs; Name: "{app}\*"

[InstallDelete]
;Type: filesandordirs; Name: "{app}\*"
Type: filesandordirs; Name: "{app}\Lib"
Type: filesandordirs; Name: "{app}\Scripts"
Type: filesandordirs; Name: "{app}\icons"
Type: filesandordirs; Name: "{app}\structurefinder"
Type: filesandordirs; Name: "{app}\python*.*"

[Tasks]

[Files]
Source: "..\src\structurefinder\*";            DestDir: "{app}\structurefinder"; Flags: ignoreversion createallsubdirs recursesubdirs
Source: "..\dist\python_dist\*";               DestDir: "{app}"; Flags: ignoreversion createallsubdirs recursesubdirs
Source: "..\icons\*";                          DestDir: "{app}\icons"; Flags: ignoreversion createallsubdirs recursesubdirs
Source: "..\structurefinder.exe";              DestDir: "{app}"; Flags: ignoreversion
Source: "..\update.exe";              DestDir: "{app}"; Flags: ignoreversion
Source: "..\vc_redist.x64.exe";                DestDir: "{app}"; Flags: ignoreversion

[Dirs]
;Name: "{app}\displaymol"; Permissions: everyone-full
;Name: "{app}\gui"; Permissions: everyone-full

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
// This procedure deletes the installer executable when it
// is named 'update-structurefinder.exe'
var
  strContent: String;
  intErrorCode: Integer;
  strSelf_Delete_BAT: String;
begin
  // Pos == str.contains(x)
  if Pos('update-structurefinder.exe', ExpandConstant('{srcexe}')) > 0 then
    begin
    if CurStep=ssDone then
    begin
      strContent := ':try_delete' + #13 + #10 +
            'del "' + ExpandConstant('{srcexe}') + '"' + #13 + #10 +
            'if exist "' + ExpandConstant('{srcexe}') + '" goto try_delete' + #13 + #10 +
            'del %0';

      strSelf_Delete_BAT := ExtractFilePath(ExpandConstant('{tmp}')) + 'SelfDelete.bat';
      SaveStringToFile(strSelf_Delete_BAT, strContent, False);
      Exec(strSelf_Delete_BAT, '', '', SW_HIDE, ewNoWait, intErrorCode);
    end;
  end;
end;
