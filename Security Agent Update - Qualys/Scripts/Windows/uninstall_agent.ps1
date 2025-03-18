$serviceName = "QualysAgent"


function Uninstall-QualysAgent {
    # Stop the service if it is running
     #Stop-Service -Name $serviceName
     
    # Delete the service
    if (Get-WmiObject -Class Win32_Service -Filter "Name='$serviceName'") {
        #sc.exe delete $serviceName
        cd "${env:ProgramFiles}\Qualys\QualysAgent"
        $unstallcmd = "Uninstall.exe Uninstall=True"
        cmd.exe /c $unstallcmd
        Start-Sleep -Seconds 5
        if ((Get-Service -Name $serviceName).Status -eq "Running") {
            Write-Host "Qualys Agent is still running."
        
        } else {
            Remove-Item -Path "C:\Windows\agents\qualys.txt"
            Write-Host "Qualys Agent service Successfully Uninstalled."
        }
        
    } else {
        Write-Host "Qualys Agent service is not installed or cannot be found."
    }
}


if (Get-Service -Name $serviceName -ErrorAction SilentlyContinue) {
    if ((Get-Service -Name $serviceName).Status -eq "Running") {
        $file = "C:\Windows\agents\qualys.txt"
        if (Test-Path $file -PathType Leaf) {
            
        Uninstall-QualysAgent
        }
    }
} else {
    Write-Host "Qualys Agent service is not installed or cannot be found. Hence Installing it."
    #install-QualysAgent
}

