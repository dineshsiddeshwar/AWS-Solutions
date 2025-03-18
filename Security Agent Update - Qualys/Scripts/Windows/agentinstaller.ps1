$serviceName = "QualysAgent"

function install-QualysAgent {
    mkdir "C:\Windows\agents"
    # $bucket = "qualys-agents-installer"
    # $key = "StateRAMP/Windows/QualysCloudAgent.exe"

    # Read-S3Object -BucketName $bucket -Key $key -File "C:\Windows\agents\QualysCloudAgent.exe" -Region us-east-1


    $CustomerId = "{XXXX}"
    $ActivationId = "{YYYY}"
    $WebServiceUri = "https://qagpublic.qg2.apps.qualys.com/CloudAgent/"

    $CmdCommand = "C:\Windows\agents\QualysCloudAgent.exe CustomerId=$CustomerId ActivationId=$ActivationId WebServiceUri=$WebServiceUri"
    cmd.exe /c $CmdCommand
    Start-Sleep -Seconds 5
    if ((Get-Service -Name $serviceName).Status -eq "Running") {
        New-Item -ItemType File -Path "C:\Windows\agents\qualys.txt"
        Write-Host "Qualys Agent service is installed and running."
    } else {
        Write-Host "Qualys Agent service is installed and not running."
    }
    Write-Host "Removing EXE files"
    Remove-Item -Path "C:\Windows\agents\QualysCloudAgent.exe"
}

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
            Write-Host "Qualys Agent for stateramp already installed hence exiting"
            exit 0
        }
        Write-Host "Qualys Agent is running. Hence Uninstalling it"
        Uninstall-QualysAgent
        install-QualysAgent
    } else {
        Write-Host "Qualys Agent service is not running."
        Uninstall-QualysAgent
        install-QualysAgent
    }
} else {
    Write-Host "Qualys Agent service is not installed or cannot be found. Hence Installing it."
    install-QualysAgent
}

