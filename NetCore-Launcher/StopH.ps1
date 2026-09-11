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


$connectionProfile =
[Windows.Networking.Connectivity.NetworkInformation]::GetInternetConnectionProfile()


if ($null -eq $connectionProfile) {

    Write-Output "No connection profile found"
    exit
}


$tetheringManager =
[Windows.Networking.NetworkOperators.NetworkOperatorTetheringManager,Windows.Networking.NetworkOperators,ContentType=WindowsRuntime]::CreateFromConnectionProfile($connectionProfile)



# Check hotspot status

$state = $tetheringManager.TetheringOperationalState


Write-Output "Current status: $state"



# Stop hotspot if running

if ($state -eq 1) {

    $result = Await(
        $tetheringManager.StopTetheringAsync()
    ) ([Windows.Networking.NetworkOperators.NetworkOperatorTetheringOperationResult])


    Write-Output "`nStopping Mobile Hotspot Network....`nHotspot stopped"
}
else {

    Write-Output "Hotspot is already stopped"
}