@echo off
echo ====================================================
echo Starting interactive NotebookLM Login...
echo ====================================================
echo.
echo NOTE: Playwright will open a Chromium window.
echo If you don't see it immediately, check your taskbar.
echo.

:: We use powershell's Start-Process to break out of invisible background Window Stations (like those used by Claude Desktop/Cursor)
powershell -WindowStyle Normal -Command "Start-Process cmd -ArgumentList '/c', 'cd /d \"%~dp0\" && venv\Scripts\notebooklm.exe login && pause'"
