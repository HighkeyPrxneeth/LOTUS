param(
  [ValidateRange(1, 65535)]
  [int]$Port = 8787
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Command tailscale -ErrorAction SilentlyContinue)) {
  throw 'Install and sign in to Tailscale on the laptop and phone before starting phone access.'
}

try {
  Invoke-WebRequest -Uri "http://127.0.0.1:$Port/" -UseBasicParsing -TimeoutSec 5 | Out-Null
} catch {
  throw "LOTUS is not responding on 127.0.0.1:$Port. Start the built Fabric profile first."
}

$tailnet = tailscale status --json | ConvertFrom-Json
if ($LASTEXITCODE -ne 0 -or $tailnet.BackendState -ne 'Running') {
  throw 'Tailscale is not connected. Sign in on the laptop, then run this script again.'
}

tailscale serve --bg $Port
if ($LASTEXITCODE -ne 0) {
  throw 'Tailscale Serve could not expose the local LOTUS app.'
}

$name = ([string]$tailnet.Self.DNSName).TrimEnd('.')
if (-not $name) {
  throw 'Tailscale did not return a device DNS name. Check MagicDNS and HTTPS in your tailnet.'
}

Write-Output "Phone patient page: https://$name/patient"
Write-Output "Phone prescriber login: https://$name/login"
Write-Output 'Open the link only on a device signed in to the same tailnet. Test camera and vault access before presenting.'
