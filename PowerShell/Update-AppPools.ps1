
foreach ($server in (Get-Content "servers.txt")) {
    Write-Host $server
    Invoke-Command -ComputerName $server -ScriptBlock {
        Import-Module WebAdministration
        
        ####
        # Get the private key file used for Care Everywhere
        ####

        # Get the Certificate for Care Everywhere
        $commonName = "CETRAINING"
        $workingCert = Get-ChildItem CERT:\LocalMachine\My | where {$_.Subject -match $commonName} | sort $_.NotAfter -Descending | select -first 1 -erroraction STOP
        $thumbprint = $workingCert.Thumbprint
        $rsaFile = $workingCert.PrivateKey.CspKeyContainerInfo.UniqueKeyContainerName

        # Get the certificate file and its access rights
        $certRoot = "c:\programdata\microsoft\crypto\rsa\machinekeys\"
        $certPath = $certRoot+$rsaFile
        $acl = Get-Acl -Path $certPath

	    ############################################
	    # Create and configure any missing App Pools
	    ############################################
	    $iisAppPoolNameTemplate = "Interconnect-train"
        $iisAppPoolDotNetVersion = "v4.0"

        # navigate to the App Pools root
        cd IIS:\AppPools\

        for ($i=1; $i -le 50; $i++) {
            #get the name for the app pool
            if ($i -lt 10) { $iisAppPoolName = $("{0}0{1}" -f $iisAppPoolNameTemplate,$i) }
            else { $iisAppPoolName = $("{0}{1}" -f $iisAppPoolNameTemplate,$i) }

            # check if the app pool exists
            if (!(Test-Path $iisAppPoolName -pathType container)) {
                # create the app pool if it doesn't
                Write-Host "Creating $iisAppPoolName"
                $appPool = New-Item $iisAppPoolName
                }
            # Otherwise, get the existing App Pool
            else {
                $appPool = Get-Item $iisAppPoolName
                }

            # Set the necessary properties of the App Pool
            Write-Host "Updating $iisAppPoolName"
            $appPool.Stop()
            $appPool | Set-ItemProperty -Name "managedRuntimeVersion" -Value $iisAppPoolDotNetVersion
            $appPool | Set-ItemProperty -Name "enable32BitAppOnWin64" -Value $true
            $appPool.Start()

            ####
            # Make sure the App Pool identity can access the private key
            ####

            # Get the App Pool identity
            $identity = $appPool.processModel
            #if identity.userName is empty, use 'IIS AppPool\AppPoolNameHere'
            $poolUser = "IIS AppPool\$iisAppPoolName"
            #else, use that userName

            # if our poolUser is not in the acl.Access, add a rule
            $permission="$poolUser","Read","Allow"
            $accessRule=new-object System.Security.AccessControl.FileSystemAccessRule $permission
            Write-Host "Giving $poolUser access to $commonName"
            $acl.AddAccessRule($accessRule)
            $acl.Access | Format-Table -AutoSize
            }

        # Make sure to commit the changes to the cert file's access rights
        Set-Acl $certPath $acl

	    #####################################################
	    # Assign Interconnects to their respective App Pools
	    #####################################################
        cd 'IIS:\Sites\Default Web Site'
		Get-Item "Interconnect-train*" | ForEach-Object {
            $interconnectPath = Split-Path $_.physicalPath -Parent
            $interconnect = Split-Path $interconnectPath -Leaf
            $appPath = $_.Path
            Set-ItemProperty "IIS:\Sites\Default Web Site\$appPath" applicationPool $interconnect
            $setPool = $(Get-ItemProperty "IIS:\Sites\Default Web Site\$appPath" applicationPool).Value
            Write-Host "$appPath set to $setPool"
            }
        }
    }