param(
  [string]$BucketUri = "s3://nahuatl-language/molina/databases",
  [string]$Region = "us-east-1",
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

$artifacts = @(
  @{ Local = "lexicon_bootstrap/fcn_master_lexicon.sqlite"; Key = "fcn_master_lexicon.sqlite" },
  @{ Local = "orthography/fcn_master_lexicon_phase6_review.sqlite"; Key = "fcn_master_lexicon_phase6_review.sqlite" },
  @{ Local = "core_vocabulary/fcn_master_lexicon_phase7_review (1).sqlite"; Key = "fcn_master_lexicon_phase7_review.sqlite" },
  @{ Local = "curriculum/fcn_master_lexicon_phase8_bootstrap.sqlite"; Key = "fcn_master_lexicon_phase8_bootstrap.sqlite" },
  @{ Local = "curriculum/fcn_master_lexicon_phase8_open_only.sqlite"; Key = "fcn_master_lexicon_phase8_open_only.sqlite" },
  @{ Local = "curriculum/fcn_master_lexicon_phase8_1_clean.sqlite"; Key = "fcn_master_lexicon_phase8_1_clean.sqlite" },
  @{ Local = "curriculum/fcn_master_lexicon_phase8_2_units.sqlite"; Key = "fcn_master_lexicon_phase8_2_units.sqlite" },
  @{ Local = "curriculum/fcn_master_lexicon_phase8_3_exports.sqlite"; Key = "fcn_master_lexicon_phase8_3_exports.sqlite" },
  @{ Local = "curriculum/fcn_master_lexicon_phase8_4_assessment.sqlite"; Key = "fcn_master_lexicon_phase8_4_assessment.sqlite" },
  @{ Local = "curriculum/fcn_master_lexicon_phase8_5_products.sqlite"; Key = "fcn_master_lexicon_phase8_5_products.sqlite" },
  @{ Local = "curriculum/fcn_master_lexicon_phase8_6_primer.sqlite"; Key = "fcn_master_lexicon_phase8_6_primer.sqlite" }
)

foreach ($artifact in $artifacts) {
  $localPath = Join-Path $repoRoot $artifact.Local
  if (-not (Test-Path -LiteralPath $localPath)) {
    throw "Missing artifact: $localPath"
  }

  $target = "$BucketUri/$($artifact.Key)"
  if ($DryRun) {
    Write-Output "DRY RUN: aws s3 cp `"$localPath`" `"$target`" --region $Region --content-type application/vnd.sqlite3"
  } else {
    aws s3 cp $localPath $target --region $Region --content-type application/vnd.sqlite3
  }
}
