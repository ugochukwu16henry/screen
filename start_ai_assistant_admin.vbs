Set UAC = CreateObject("Shell.Application")
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the directory where this script is located
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
pythonScript = scriptDir & "\ai_screen_assistant.py"

' Check if Python is in PATH, if not try common locations
pythonCmd = "python"
On Error Resume Next
WshShell.Run "python --version", 0, True
If Err.Number <> 0 Then
    ' Try common Python locations
    If fso.FileExists("C:\Python\python.exe") Then
        pythonCmd = "C:\Python\python.exe"
    ElseIf fso.FileExists("C:\Program Files\Python\python.exe") Then
        pythonCmd = "C:\Program Files\Python\python.exe"
    End If
End If
On Error GoTo 0

' Request administrator privileges and run Python script
' runas = request admin, 1 = show window
UAC.ShellExecute pythonCmd, "ai_screen_assistant.py", scriptDir, "runas", 1

Set UAC = Nothing
Set WshShell = Nothing
Set fso = Nothing
