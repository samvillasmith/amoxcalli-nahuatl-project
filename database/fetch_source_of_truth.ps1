param(
  [string]$SourceUrl = "https://nahuatl-language.s3.us-east-1.amazonaws.com/molina/databases/fcn_master_lexicon_phase8_6_primer.sqlite",
  [string]$OutPath = ".\database\fcn_master_lexicon_phase8_6_primer.sqlite"
)

$ErrorActionPreference = "Stop"
$target = Resolve-Path -Path (Split-Path $OutPath -Parent) -ErrorAction SilentlyContinue
if (-not $target) {
  New-Item -ItemType Directory -Path (Split-Path $OutPath -Parent) | Out-Null
}

Invoke-WebRequest -Uri $SourceUrl -OutFile $OutPath

$size = (Get-Item -LiteralPath $OutPath).Length
Write-Output "Downloaded source-of-truth database to $OutPath ($size bytes)."
