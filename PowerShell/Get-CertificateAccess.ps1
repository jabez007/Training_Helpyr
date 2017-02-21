
foreach ($server in (Get-Content "servers.txt")) {
    Write-Host $server
    Invoke-Command -ComputerName $server -ScriptBlock {
        # Get the Certificate for Care Everywhere
        $commonName = "CETRAINING"
        $workingCert = Get-ChildItem CERT:\LocalMachine\My | where {$_.Subject -match $commonName} | sort $_.NotAfter -Descending | select -first 1 -erroraction STOP
        $thumbprint = $workingCert.Thumbprint
        $rsaFile = $workingCert.PrivateKey.CspKeyContainerInfo.UniqueKeyContainerName

        # Get and check rights on certificate file
        $certRoot = "c:\programdata\microsoft\crypto\rsa\machinekeys\"
        $certPath = $certRoot+$rsaFile
        $acl = Get-Acl -Path $certPath
        $acl.Access | Format-Table -AutoSize
        }
    }
