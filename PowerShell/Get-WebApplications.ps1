Param( #Must be the first statement in your script
	[string]$serversFile
	) 

	Invoke-Command -ComputerName icx82-trnce01 -ScriptBlock {
		Import-Module WebAdministration
		Get-WebApplication -Site "Default Web Site" -Name "Interconnect-train*" | ForEach-Object {$_; Write-Host "# # # #"}
		} #| Export-CSV results.csv

	#Read-Host -Prompt "Press Enter to exit"