# Install missing dependencies
$pythonExe = "C:\Users\ONE CLICK\AppData\Local\Programs\Python\Python314\python.exe"

Write-Host "Installing dependencies..."
& $pythonExe -m pip install --quiet --upgrade pip

Write-Host "Installing python-jose..."
& $pythonExe -m pip install --quiet python-jose

Write-Host "Installing passlib..."
& $pythonExe -m pip install --quiet passlib

Write-Host "Installing cryptography..."  
& $pythonExe -m pip install --quiet cryptography

Write-Host "Installing email-validator..."
& $pythonExe -m pip install --quiet email-validator

Write-Host "Installation complete!"
