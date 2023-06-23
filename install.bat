@echo off

echo "The installer requires Internet connectivity to download Python packages listed in the requirements.txt file."
echo.
echo "Check Internet connectivity before continuing installation."
echo.
echo.
pause

echo "Creating Python Virtual Environment"
echo.
echo "This may take a minute. Please wait..."
start /b /W python -m venv venv

echo.
echo "Virtual Environment 'venv' creation complete"
echo.

call .\venv\Scripts\activate.bat
echo.
echo "Installing required Python packages."
echo "Please wait...
echo.
start /W pip install -r requirements.txt
pause
