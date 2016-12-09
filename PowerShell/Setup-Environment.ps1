Param( #Must be the first statement in your script
    [string]$cache, 
	[string]$interconnect
	)

WorkFlow Setup-Environment {

    Param( #Must be the first statement in your script
	    [string]$cache, 
	    [string]$interconnect
	    )

	ForEach -Parallel ($server in (Get-Content "servers.txt")) {

		$found = InlineScript {
            $found = Invoke-Command -ComputerName $Using:server -ScriptBlock {
			    param($cache)
			    Import-Module WebAdministration
			    Get-WebApplication -Site "Default Web Site" -Name "Interconnect-train$cache"
			    } -ArgumentList $Using:cache -ErrorAction stop
            $found
            }

		if ($found) {
			Add-Content "setup.err" "Web Application Interconnect-train$cache already exists`n"
			exit 1
			}

		Copy-Item "F:\Care Everywhere\Community\Training\MRIP_Training\Refresh\Net_Configs\net$cache.config" "\\$server\C$\Epic\Instances\Interconnect-train$interconnect\web\app_data\config\net.config" -erroraction stop
		Copy-Item "F:\Care Everywhere\Community\Training\MRIP_Training\Refresh\CE_Configs\CareEverywhere.config_Interconnect-Train$cache.config" "\\$server\C$\Epic\Instances\Interconnect-train$interconnect\web\app_data\config\CareEverywhere.config" -erroraction stop
		Copy-Item "F:\Care Everywhere\Community\Training\MRIP_Training\Refresh\CE_Configs\RoleSpecificWcfConfig.config_Interconnect-Train$cache.config" "\\$server\C$\Epic\Instances\Interconnect-train$interconnect\web\app_data\config\RoleSpecificWcfConfig.config" -erroraction stop
		Copy-Item "F:\Care Everywhere\Community\Training\MRIP_Training\Refresh\CE_Configs\Web.config_Interconnect-Train$cache.config" "\\$server\C$\Epic\Instances\Interconnect-train$interconnect\web\wcf\Web.config" -erroraction stop

		InlineScript {
            Invoke-Command -ComputerName $Using:server -ScriptBlock {
			    param($cache,$interconnect)			
			    Import-Module WebAdministration
			    New-WebApplication -Name "Interconnect-train$cache"  -Site "Default Web Site" -PhysicalPath "C:\Epic\Instances\Interconnect-train$interconnect\web" -ApplicationPool "Interconnect-train$interconnect"
			    Start-Service -name "Interconnect-train$interconnect"
			    } -ArgumentList $Using:cache,$Using:interconnect -erroraction stop
            }
		}
    }

Setup-Environment -interconnect $interconnect -cache $cache
#Read-Host -Prompt "Press Enter to exit"
exit $LASTEXITCODE
