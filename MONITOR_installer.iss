#define MyAppName "MONITOR"
#define MyAppVersion "1.0"
#define MyAppPublisher "Your Company"
#define MyAppExeName "MONITOR_app.exe"
#define MyAppURL "https://www.yourcompany.com"
#define MyAppSupportURL "https://www.yourcompany.com/support"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
AppId={{8F7D3B9A-1E5C-4F2D-9B8A-3C6D5E4F2A1B}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppSupportURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=MONITOR_README.txt
OutputDir=installer
OutputBaseFilename=MONITOR_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
MinVersion=10.0.17763

[Languages]
Name: "german"; MessagesFile: "compiler:Languages\German.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Main application files
Source: "dist\MONITOR_app.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\playwright_browsers\*"; DestDir: "{app}\playwright_browsers"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\data\*"; DestDir: "{app}\data"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "MONITOR_README.txt"; DestDir: "{app}"; Flags: ignoreversion

; Static files
Source: "static\*"; DestDir: "{app}\static"; Flags: ignoreversion recursesubdirs createallsubdirs

; Python environment and dependencies
Source: "Scripts\*"; DestDir: "{app}\Scripts"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Lib\*"; DestDir: "{app}\Lib"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Include\*"; DestDir: "{app}\Include"; Flags: ignoreversion recursesubdirs createallsubdirs

; Cache files
// Source: "monitor_temp_cache.json"; DestDir: "{app}"; Flags: ignoreversion
// Source: "monitor_waterlevel_cache.json"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: files; Name: "{app}\MONITOR_debug.log"
Type: files; Name: "{app}\monitor_temp_cache.json"
Type: files; Name: "{app}\monitor_waterlevel_cache.json"

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Create necessary directories if they don't exist
    ForceDirectories(ExpandConstant('{app}\static'));
    ForceDirectories(ExpandConstant('{app}\logs'));
  end;
end; 