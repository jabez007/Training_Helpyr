Invoke-Command -ComputerName cedev-phonebook -ScriptBlock {
	Restart-Service -name "Interconnect-train"
	}