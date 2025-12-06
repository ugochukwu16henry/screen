Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Path to the launcher
launcherPath = scriptDir & "\start_ai_assistant_admin.vbs"

' Create shortcut on desktop first (easier to pin from there)
desktopPath = WshShell.SpecialFolders("Desktop")
shortcutPath = desktopPath & "\AI Screen Assistant.lnk"

Set shortcut = WshShell.CreateShortcut(shortcutPath)
shortcut.TargetPath = launcherPath
shortcut.WorkingDirectory = scriptDir
shortcut.Description = "AI Screen Assistant - Local AI for Screen OCR"
shortcut.IconLocation = "python.exe,0"  ' Use Python icon
shortcut.Save

WScript.Echo "Shortcut created on desktop: " & shortcutPath
WScript.Echo ""
WScript.Echo "To add to taskbar:"
WScript.Echo "1. Right-click the shortcut on desktop"
WScript.Echo "2. Select 'Pin to taskbar'"
WScript.Echo ""
WScript.Echo "Or drag the shortcut to your taskbar"

Set shortcut = Nothing
Set WshShell = Nothing
Set fso = Nothing


