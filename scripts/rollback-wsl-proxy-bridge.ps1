param(
    [ValidateSet("old", "current")]
    [string]$Target = "old"
)

$listenAddress = "172.31.80.1"
$listenPort = "17892"
$connectPort = if ($Target -eq "current") { "7897" } else { "7892" }

netsh interface portproxy delete v4tov4 `
    listenaddress=$listenAddress listenport=$listenPort | Out-Null
netsh interface portproxy add v4tov4 `
    listenaddress=$listenAddress listenport=$listenPort `
    connectaddress=127.0.0.1 connectport=$connectPort

Write-Output "WSL proxy bridge: $listenAddress`:$listenPort -> 127.0.0.1`:$connectPort"
