Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Change to the script directory and run Python
WshShell.CurrentDirectory = scriptDir
WshShell.Run "python ai_screen_assistant.py", 0, False

Set WshShell = Nothing
Set fso = Nothing

