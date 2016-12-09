Param( #Must be the first statement in your script
	[string]$installDir,
	[string]$instanceDir
	)

	$installHelper = Join-Path -Path $installDir -ChildPath "Interconnect\InstallHelper.exe"
	if (Test-Path $installHelper) {
		Write-Host "Using $installHelper"
		$instances = dir $instanceDir | ?{$_.PSISContainer}
		Foreach ($i in $instances) {
			$fullPath = $i.FullName
			$testpath = Join-Path -Path $fullPath -ChildPath "InstallHelper.exe"
			if (Test-Path $testpath) {
				Write-Host "Updating $fullPath"
				& $InstallHelper /up $fullPath | Out-Null
				}
			}
		}
	
	Read-Host -Prompt "Press Enter to Continue"