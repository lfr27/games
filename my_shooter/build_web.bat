@echo off
echo Building web version...
"C:\Users\luisf\AppData\Roaming\Python\Python314\Scripts\pygbag.exe" --build --disable-sound-format-error .
if errorlevel 1 (echo Build failed! & exit /b 1)

echo Patching background color...
powershell -Command "(Get-Content 'build\web\index.html') -replace 'body\.style\.background = \"#7f7f7f\"', 'body.style.background = \"#000000\"' | Set-Content 'build\web\index.html'"

echo Deploying to the-final-wave branch...
cd ..
git checkout the-final-wave
copy /y my_shooter\build\web\index.html index.html
copy /y my_shooter\build\web\favicon.png favicon.png
copy /y my_shooter\build\web\my_shooter.apk my_shooter.apk
copy /y my_shooter\build\web\my_shooter.tar.gz my_shooter.tar.gz
git add index.html favicon.png my_shooter.apk my_shooter.tar.gz
git commit -m "Update web build"
git push origin the-final-wave
git checkout main
cd my_shooter

echo Done! Live at https://lfr27.github.io/games/
