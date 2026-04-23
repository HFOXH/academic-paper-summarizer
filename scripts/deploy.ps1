param(
    [string]$Environment = "dev",   # dev | test | prod
    [string]$ProjectName = "twin"
)

$ErrorActionPreference = "Stop"

Write-Host "Deploying $ProjectName to $Environment ..." -ForegroundColor Green


# =========================
# 1. BACKEND BUILD (Lambda)
# =========================
Write-Host "Building Lambda package..." -ForegroundColor Yellow

Set-Location (Join-Path $PSScriptRoot "..\backend")

python deploy.py

Set-Location ..

Write-Host "Lambda package ready." -ForegroundColor Green


# =========================
# 2. TERRAFORM INIT + APPLY
# =========================
Write-Host "Running Terraform..." -ForegroundColor Yellow

Set-Location terraform

if (-not (Test-Path ".terraform")) {
    terraform init -input=false
}

$workspaces = terraform workspace list

if ($workspaces -notmatch $Environment) {
    terraform workspace new $Environment
} else {
    terraform workspace select $Environment
}

terraform apply `
    -var="project_name=$ProjectName" `
    -var="environment=$Environment" `
    -auto-approve

# outputs
$ApiUrl = terraform output -raw api_gateway_url
$FrontendBucket = terraform output -raw frontend_bucket
$CfUrl = terraform output -raw cloudfront_url

try {
    $CustomUrl = terraform output -raw custom_domain_url
} catch {
    $CustomUrl = ""
}

Set-Location ..

Write-Host "Terraform applied." -ForegroundColor Green


# =========================
# 3. FRONTEND BUILD + DEPLOY
# =========================
Write-Host "Building frontend..." -ForegroundColor Yellow

Set-Location frontend

# API URL for frontend
"NEXT_PUBLIC_API_URL=$ApiUrl" | Out-File .env.production -Encoding utf8

npm install
npm run build

if (-not (Test-Path ".\out\index.html")) {
    throw "Build failed: index.html not found in /out. Check Next.js config (output: export)."
}

aws s3 sync .\out "s3://$FrontendBucket/" --delete

# =========================
# 3.1 CLOUD FRONT INVALIDATION (IMPORTANT)
# =========================
Write-Host "Invalidating CloudFront cache..." -ForegroundColor Yellow

aws cloudfront create-invalidation `
  --distribution-id E2PAXNW1LX70K `
  --paths "/*"

Write-Host "CloudFront invalidated." -ForegroundColor Green

Set-Location ..

Write-Host "Frontend deployed." -ForegroundColor Green


# =========================
# 4. FINAL OUTPUT
# =========================
Write-Host "`n=========================" -ForegroundColor Cyan
Write-Host "DEPLOY COMPLETE" -ForegroundColor Green
Write-Host "=========================`n" -ForegroundColor Cyan

Write-Host "CloudFront URL : $CfUrl" -ForegroundColor Cyan

if ($CustomUrl) {
    Write-Host "Custom domain  : $CustomUrl" -ForegroundColor Cyan
}

Write-Host "API Gateway    : $ApiUrl" -ForegroundColor Cyan