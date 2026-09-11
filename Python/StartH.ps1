[Windows.System.UserProfile.LockScreen,Windows.System.UserProfile,ContentType=WindowsRuntime] | Out-Null

Add-Type -AssemblyName System.Runtime.WindowsRuntime

$asTaskGeneric = ([System.WindowsRuntimeSystemExtensions].GetMethods() |
    Where-Object {
        $_.Name -eq 'AsTask' -and
        $_.GetParameters().Count -eq 1 -and
        $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
    })[0]


Function Await($WinRtTask, $ResultType) {
    $asTask = $asTaskGeneric.MakeGenericMethod($ResultType)
    $netTask = $asTask.Invoke($null, @($WinRtTask))
    $netTask.Wait(-1) | Out-Null
    $netTask.Result
}


Function AwaitAction($WinRtAction) {
    $asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() |
        Where-Object {
            $_.Name -eq 'AsTask' -and
            $_.GetParameters().Count -eq 1 -and
            !$_.IsGenericMethod
        })[0]

    $netTask = $asTask.Invoke($null, @($WinRtAction))
    $netTask.Wait(-1) | Out-Null
}


# Get current network connection
$connectionProfile = [Windows.Networking.Connectivity.NetworkInformation,Windows.Networking.Connectivity,ContentType=WindowsRuntime]::GetInternetConnectionProfile()


if ($null -eq $connectionProfile) {
    Write-Output "ERROR: No internet connection found"
    exit
}


# Create Mobile Hotspot manager
$tetheringManager = [Windows.Networking.NetworkOperators.NetworkOperatorTetheringManager,Windows.Networking.NetworkOperators,ContentType=WindowsRuntime]::CreateFromConnectionProfile($connectionProfile)


# Configure hotspot
$config = $tetheringManager.GetCurrentAccessPointConfiguration()

$config.Ssid = "ssid"
$config.Passphrase = "password"

AwaitAction(
    $tetheringManager.ConfigureAccessPointAsync($config)
)


# Toggle hotspot

$state = $tetheringManager.TetheringOperationalState


# Hotspot is ON
if ($state -eq 1) {

    Write-Output "Stopping Mobile Hotspot..."

    $result = Await (
        $tetheringManager.StopTetheringAsync()
    ) ([Windows.Networking.NetworkOperators.NetworkOperatorTetheringOperationResult])


    if ($result.Status -eq "Success") {
        Write-Output "SUCCESS: Mobile Hotspot stopped"
    }
    else {
        Write-Output "ERROR: Failed to stop hotspot"
        Write-Output $result.AdditionalErrorMessage
    }

}


# Hotspot is OFF
else {

    Write-Output "Starting Mobile Hotspot..."

    $result = Await (
        $tetheringManager.StartTetheringAsync()
    ) ([Windows.Networking.NetworkOperators.NetworkOperatorTetheringOperationResult])


    if ($result.Status -eq "Success") {
        Write-Output "SUCCESS: Mobile Hotspot started"
    }
    else {
        Write-Output "ERROR: Failed to start hotspot"
        Write-Output $result.AdditionalErrorMessage
    }

}