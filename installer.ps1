# Make sure we are running as Admin
If (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")){   
    $arguments = "& '" + $myinvocation.mycommand.definition + "'"
    Start-Process powershell -Verb runAs -ArgumentList $arguments
    Break
    }

bitsadmin.exe /transfer "Python Download" https://www.python.org/ftp/python/2.7.13/python-2.7.13.msi "$ENV:UserProfile\Downloads\python-2.7.13.msi"

Start-Process "msiexec" -ArgumentList "/i","$ENV:UserProfile\Downloads\python-2.7.13.msi","/qb","ALLUSERS=1","ADDLOCAL=ALL" -NoNewWindow -Wait

$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User") 

pip install -r "$PSScriptRoot\requirements.txt"

New-Service -name TrainingHelpyr -binaryPathName "python ""$PSScriptRoot\run_webapp.py""" -displayName "Training Helpyr" -StartupType Automatic -Description "Runs the web interface for the Training Helpyr"

Read-Host "Press to continue..."
