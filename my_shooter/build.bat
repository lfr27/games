cd C:\GitHub\games\my_shooter
python -m PyInstaller --onefile --noconsole --add-data "assets;assets" main.py
echo Build complete! Check the dist folder.
pause