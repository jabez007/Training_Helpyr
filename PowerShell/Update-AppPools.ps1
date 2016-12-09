
foreach ($server in (Get-Content "servers.txt")) {
    Write-Host $server
    Invoke-Command -ComputerName $server -ScriptBlock {
	    	Import-Module WebAdministration

	    	###############################
	    	# Create any missing App Pools
	    	###############################
	    	$iisAppPoolNameTemplate = "Interconnect-train"
            $iisAppPoolDotNetVersion = "v4.0"

            # navigate to the app pools root
            cd IIS:\AppPools\

            for ($i=1; $i -le 50; $i++) {
                #get the name for the app pool
                if ($i -lt 10) { $iisAppPoolName = $("{0}0{1}" -f $iisAppPoolNameTemplate,$i) }
                else { $iisAppPoolName = $("{0}{1}" -f $iisAppPoolNameTemplate,$i) }

                # check if the app pool exists
                if (!(Test-Path $iisAppPoolName -pathType container)) {
                    # create the app pool
                    Write-Host $iisAppPoolName
                    $appPool = New-Item $iisAppPoolName
                    $appPool | Set-ItemProperty -Name "managedRuntimeVersion" -Value $iisAppPoolDotNetVersion
                    $appPool | Set-ItemProperty -Name "enable32BitAppOnWin64" -Value $true
                    }
                }

	    	#####################################################
	    	# Assign Interconnects to their respective App Pools
	    	#####################################################
		    Get-WebApplication -Site "Default Web Site" -Name "Interconnect-train*" | ForEach-Object {
                $interconnectPath = Split-Path $_.PhysicalPath -Parent
                $interconnect = Split-Path $interconnectPath -Leaf
                $appPath = $_.Path
                Set-ItemProperty "IIS:\Sites\Default Web Site\$appPath" applicationPool $interconnect
                Write-Host $(Get-ItemProperty "IIS:\Sites\Default Web Site\$appPath" applicationPool).Value}
            }
    }