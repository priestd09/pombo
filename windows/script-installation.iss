; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

; Derni�re modif le 14/01/2010.

#define MyAppName "Pombo"
#define MyAppVersion "0.0.9"
#define MyAppPublisher "BoboTiG"
#define MyAppURL "http://bobotig.fr"

; Constante perso pour d�finir le dossier dans lequel se trouve le
; dossier pombo-$version.
#define MyAppSDir "C:\Users\T2\Documents\"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{D24DCF9D-1F2E-4846-A4DF-0A41E13E4472}
AppCopyright=Copyleft 2012 {#MyAppPublisher}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppReadmeFile={#MyAppURL}
AppSupportURL={#MyAppURL}/contenu/projets/pombo
AppUpdatesURL={#MyAppURL}
DefaultDirName=C:\pombo
DefaultGroupName={#MyAppName}
DisableDirPage=yes
DisableProgramGroupPage=yes
InfoAfterFile={#MyAppSDir}pombo-{#MyAppVersion}\POSTINSTALL
LicenseFile={#MyAppSDir}\pombo-{#MyAppVersion}\LICENSE
OutputDir={#MyAppSDir}\pombo-{#MyAppVersion}
OutputBaseFilename=pombo-{#MyAppVersion}_setup
PrivilegesRequired=admin
SetupIconFile={#MyAppSDir}\pombo-{#MyAppVersion}\python\DLLs\py.ico
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={#MyAppSDir}\pombo-{#MyAppVersion}\python\DLLs\py.ico
UninstallDisplayName={#MyAppName} {#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Dirs]
Name: "{app}\pngnq"
Name: "{app}\python"

[Files]
;Source: "{#MyAppSDir}pombo-{#MyAppVersion}\gpg4win-light-2.1.0.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppSDir}pombo-{#MyAppVersion}\ajouter-ip.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppSDir}pombo-{#MyAppVersion}\CREDITS"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppSDir}pombo-{#MyAppVersion}\INSTALL"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppSDir}pombo-{#MyAppVersion}\LICENSE"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppSDir}pombo-{#MyAppVersion}\pombo.conf"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppSDir}pombo-{#MyAppVersion}\pombo.php"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppSDir}pombo-{#MyAppVersion}\pombo.py"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppSDir}pombo-{#MyAppVersion}\pombo.vbs"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppSDir}pombo-{#MyAppVersion}\pngnq\*"; DestDir: "{app}\pngnq"; Flags: ignoreversion
Source: "{#MyAppSDir}pombo-{#MyAppVersion}\python\*"; DestDir: "{app}\python"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#MyAppSDir}pombo-{#MyAppVersion}\REQUIREMENTS"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppSDir}pombo-{#MyAppVersion}\test-pombo.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppSDir}pombo-{#MyAppVersion}\VERSION"; DestDir: "{app}"; Flags: ignoreversion
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Registry]
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "Pombo"; ValueData: "{app}\pombo.vbs"; Flags: deletekey uninsdeletekey

; Programmes � installer avant la bo�te de dialogue de fin
;[Run]
;Filename: "{app}\gpg4win-light-2.1.0.exe"; StatusMsg: "Install (if not already installed) GnuPG to encrypt reports."
