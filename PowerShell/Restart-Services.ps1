
foreach ($server in (Get-Content "servers.txt")) {
    Write-Host $server

    $remote = New-PSSession -ComputerName $server

    Invoke-Command -Session $remote -ScriptBlock {
        Import-Module WebAdministration
        Get-WebApplication -Site "Default Web Site" -Name "Interconnect-train*" | ForEach-Object {
            Stop-Service $_.applicationPool
            Start-Service $_.applicationPool
            }
        }
    }