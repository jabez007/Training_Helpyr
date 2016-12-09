Param( #Must be the first statement in your script
    [string]$cache, 
	[string]$interconnect
	)

WorkFlow Cleanup-Environment {

    Param( #Must be the first statement in your script
	    [string]$cache, 
	    [string]$interconnect
	    )

    ForEach -Parallel ($server in (Get-Content "servers.txt")) {
        
        InlineScript {
            Invoke-Command -ComputerName $Using:server -ScriptBlock {
		        param($cache,$interconnect)
		        Import-Module WebAdministration
		        Stop-Service -name "Interconnect-train$interconnect"
		        Remove-WebApplication -Name Interconnect-train$cache  -Site "Default Web Site"
		        } -ArgumentList $Using:cache,$Using:interconnect -erroraction stop
            }
        }
    }

Cleanup-Environment -interconnect $interconnect -cache $cache
#Read-Host -Prompt "Press Enter to exit"
exit $LASTEXITCODE
