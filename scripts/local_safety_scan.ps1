# Local Safety Scanner for WebAgentRuntimeBench
# Scans demo code only for sensitive patterns.
# Docs may mention forbidden patterns in safety-boundary context — that is expected.
# This script does NOT scan itself.

param(
    [string]$TargetDir = "."
)

$ErrorActionPreference = "Continue"
$Pass = $true
$TargetDir = Resolve-Path $TargetDir

Write-Host "=== WebAgentRuntimeBench Local Safety Scan ===" -ForegroundColor Cyan
Write-Host "Target: $TargetDir (demo code only)"
Write-Host ""

function Test-Pattern($Pattern, $Label, [string[]]$Paths) {
    Write-Host "--- Check: $Label ---" -ForegroundColor Yellow
    $found = @()
    foreach ($p in $Paths) {
        $fullPath = Join-Path $TargetDir $p
        if (Test-Path $fullPath) {
            $matches = Get-ChildItem -Path $fullPath -Recurse -File -ErrorAction SilentlyContinue |
                       Where-Object { $_.FullName -notlike "*\__pycache__\*" -and $_.Extension -ne ".pyc" } |
                       Where-Object { $_.FullName -notlike "*\scripts\*" } |
                       Select-String -Pattern $Pattern -ErrorAction SilentlyContinue
            # Filter out comments/context lines that are safety disclaimers
            $filtered = @()
            foreach ($m in $matches) {
                $line = $m.Line.Trim()
                # Skip lines clearly in safety-disclaimer or requirement-listing context
                if ($line -match "^(Not a |No |not a |never |Note: )") { continue }
                if ($line -match "^- \*\*No ") { continue }
                if ($line -match "\[x\] No ") { continue }
                if ($m.Path -match "\.md$" -and $line -match "(not store|must not|do not|Do not|Blocked|blocked|forbidden|unsafe|local-only|sanitized-only|no upload|no cloud|no external|without)") { continue }
                $filtered += $m
            }
            $found += $filtered
        }
    }
    if ($found.Count -gt 0) {
        Write-Host "[FAIL] Found in code:" -ForegroundColor Red
        $found | ForEach-Object { Write-Host "  $($_.Path):$($_.LineNumber) — $($_.Line.Trim())" -ForegroundColor Red }
        $script:Pass = $false
    } else {
        Write-Host "[OK] Clean" -ForegroundColor Green
    }
}

function Test-Pattern-Docs($Pattern, $Label) {
    Write-Host "--- Check (docs only): $Label ---" -ForegroundColor Yellow
    $docsPath = Join-Path $TargetDir "docs"
    $readmePath = Join-Path $TargetDir "README.md"
    $mdFiles = @()
    if (Test-Path $docsPath) {
        $mdFiles += Get-ChildItem -Path $docsPath -Recurse -File -Filter "*.md" -ErrorAction SilentlyContinue
    }
    if (Test-Path $readmePath) {
        $mdFiles += Get-Item $readmePath -ErrorAction SilentlyContinue
    }
    $found = $mdFiles | Select-String -Pattern $Pattern -ErrorAction SilentlyContinue
    $violations = @()
    foreach ($m in $found) {
        $line = $m.Line.Trim()
        # In docs, the pattern is acceptable in safety-boundary / forbidden context
        if ($line -match "^(.*\b(Forbidden|forbidden|blocked|Unsafe|unsafe|unsupported|does not provide|does not upload|no upload|no active probe|no bypass|no evasion|not a|Not a|never|safety|Safety|audit)\b.*)$") {
            Write-Host "  [OK] expected in safety context: $($m.Path):$($m.LineNumber)" -ForegroundColor Gray
        } elseif ($line -match "failure doctor" -and $line -match "debugging") {
            Write-Host "  [OK] product announcement context: $($m.Path):$($m.LineNumber)" -ForegroundColor Gray
        } elseif ($line -match "^- .*(not a|no |No |NOT |stop)" -or $line -match "^\\|.*\\|.*(not a|no |no.*crawler|not for)" -or $line -match "Production crawler|production crawler" -or $line -match "real.platform.scraper") {
            Write-Host "  [OK] disclaimer table row: $($m.Path):$($m.LineNumber)" -ForegroundColor Gray
        } else {
            $violations += $m
        }
    }
    if ($violations.Count -gt 0) {
        Write-Host "[FAIL] Unexpected usage in docs:" -ForegroundColor Red
        $violations | ForEach-Object { Write-Host "  $($_.Path):$($_.LineNumber) — $($_.Line.Trim())" -ForegroundColor Red }
        $script:Pass = $false
    } else {
        Write-Host "[OK] Clean or only in expected safety context" -ForegroundColor Green
    }
}

# 1. API Key leak — scan demo code only
Test-Pattern -Pattern "sk-" -Label "API Key (sk-)" -Paths @("demo")

# 2. Real platform signature fields — demo code only
Test-Pattern -Pattern "x-s-common|x-s[^-]|x-t[^-]" -Label "Real signature fields (x-s/x-t)" -Paths @("demo")

# 3. Real platform bypass phrases — all files
Test-Pattern -Pattern "real_signature|bypass_captcha|evade_antibot|real_platform_api" -Label "Real platform phrases" -Paths @(".", "demo", "docs", "sample_reports")

# 4. Executable network patterns — demo code only
Test-Pattern -Pattern "http://|https://|fetch\(|axios|XMLHttpRequest|WebSocket" -Label "Network patterns" -Paths @("demo")

# 5. Credential patterns — demo code only
Test-Pattern -Pattern "Cookie|Authorization|Bearer " -Label "Credential patterns" -Paths @("demo")

# 6. Visual runtime recommendation surfaces
Test-Pattern -Pattern "captcha bypass|anti-bot evasion|fingerprint spoofing|dynamic signature cracking|proxy rotation|account pool|ip pool|solve captcha|stealth recipe|human-like mouse|trajectory generator|VMP reconstruction|challenge solver|FLAG\\{" -Label "Visual runtime forbidden recommendations" -Paths @("failure_doctor\visual_runtime")
Test-Pattern -Pattern "captcha bypass|anti-bot evasion|fingerprint spoofing|dynamic signature cracking|bypass cloudflare|bypass akamai|bypass datadome|bypass perimeterx|proxy rotation|account pool|ip pool|solve captcha|stealth recipe|behavioral mimicry|VMP reconstruction|challenge solver|FLAG\\{|hook bypass" -Label "OCR evidence forbidden recommendations" -Paths @("failure_doctor\ocr_evidence", "examples\ocr_document_evidence_cases", "validation", "README.md", "README.zh-CN.md")
Test-Pattern -Pattern "captcha bypass|anti-bot evasion|fingerprint spoofing|dynamic signature cracking|bypass cloudflare|bypass akamai|bypass datadome|bypass perimeterx|proxy rotation|account pool|ip pool|solve captcha|stealth recipe|behavioral mimicry|human-like mouse|trajectory generator|VMP reconstruction|challenge solver|FLAG\\{|hook bypass|real regulated system access" -Label "Regulated/full-chain forbidden recommendations" -Paths @("failure_doctor\regulated_industry", "failure_doctor\full_chain", "examples\full_chain_agent_cases", "docs\REGULATED_INDUSTRY_WORKFLOW_PACK.md", "docs\FULL_CHAIN_AGENT_EVALUATION.md")
Test-Pattern -Pattern "captcha bypass|anti-bot evasion|fingerprint spoofing|dynamic signature cracking|bypass cloudflare|bypass akamai|bypass datadome|bypass perimeterx|proxy rotation|account pool|ip pool|solve captcha|stealth recipe|behavioral mimicry|human-like mouse|trajectory generator|VMP reconstruction|challenge solver|FLAG\\{|hook bypass|private training solution" -Label "CI/CD forbidden recommendations" -Paths @("failure_doctor\ci", "examples\ci_cd_integration", "docs\CI_CD_INTEGRATION.md")
Test-Pattern -Pattern "captcha bypass|anti-bot evasion|fingerprint spoofing|dynamic signature cracking|bypass cloudflare|bypass akamai|bypass datadome|bypass perimeterx|proxy rotation|account pool|ip pool|solve captcha|stealth recipe|behavioral mimicry|human-like mouse|trajectory generator|mouse movement generation to evade|VMP reconstruction|challenge solver|FLAG\\{|hook bypass|private training solution" -Label "Local KB forbidden recommendations" -Paths @("failure_doctor\kb", "examples\kb_cases", "docs\LOCAL_FAILURE_KNOWLEDGE_BASE.md", "docs\KB_IMPORT_EXPORT_POLICY.md", "docs\KB_SECURITY_MODEL.md", "README.md", "README.zh-CN.md", "validation")
Test-Pattern -Pattern "captcha bypass|anti-bot evasion|fingerprint spoofing|dynamic signature cracking|bypass cloudflare|bypass akamai|bypass datadome|bypass perimeterx|proxy rotation|account pool|ip pool|solve captcha|stealth recipe|behavioral mimicry|human-like mouse|trajectory generator|mouse movement generation to evade|VMP reconstruction|challenge solver|FLAG\\{|hook bypass|private training solution|raw secret in reasoning" -Label "Hybrid reasoning forbidden recommendations" -Paths @("failure_doctor\reasoning", "docs\HYBRID_EVIDENCE_REASONING.md", "docs\HYBRID_REASONING_SAFETY_MODEL.md", "docs\REASONING_PROVIDER_POLICY.md", "README.md", "README.zh-CN.md", "validation")
Test-Pattern -Pattern "captcha bypass|anti-bot evasion|fingerprint spoofing|dynamic signature cracking|bypass cloudflare|bypass akamai|bypass datadome|bypass perimeterx|proxy rotation|account pool|ip pool|solve captcha|stealth recipe|behavioral mimicry|human-like mouse|trajectory generator|mouse movement generation to evade|VMP reconstruction|challenge solver|FLAG\\{|hook bypass|private training solution|raw secret in audit" -Label "Enterprise governance forbidden recommendations" -Paths @("failure_doctor\enterprise", "docs\ENTERPRISE_GOVERNANCE.md", "docs\ENTERPRISE_RBAC.md", "docs\ENTERPRISE_AUDIT_LEDGER.md", "docs\RELEASE_NOTES_v4.1.0.md", "README.md", "README.zh-CN.md", "validation")
Test-Pattern -Pattern "captcha bypass|anti-bot evasion|fingerprint spoofing|dynamic signature cracking|bypass cloudflare|bypass akamai|bypass datadome|bypass perimeterx|proxy rotation|account pool|ip pool|solve captcha|stealth recipe|behavioral mimicry|human-like mouse|trajectory generator|mouse movement generation to evade|VMP reconstruction|challenge solver|FLAG\\{|hook bypass|private training solution|raw secret in plugin" -Label "Plugin SDK forbidden recommendations" -Paths @("failure_doctor\plugin", "examples\plugins", "templates\plugins", "docs\PLUGIN_SDK.md", "docs\PLUGIN_MANIFEST_SPEC.md", "docs\PLUGIN_PERMISSION_MODEL.md", "docs\PLUGIN_SECURITY_SANDBOX.md", "docs\PLUGIN_HOOK_API.md", "docs\PLUGIN_DEVELOPMENT_GUIDE.md", "docs\PLUGIN_VALIDATION_GUIDE.md", "docs\PLUGIN_ENTERPRISE_GOVERNANCE.md", "docs\PLUGIN_EXAMPLES.md", "docs\RELEASE_NOTES_v4.2.0.md", "README.md", "README.zh-CN.md", "validation")
Test-Pattern -Pattern "captcha bypass|anti-bot evasion|fingerprint spoofing|dynamic signature cracking|bypass cloudflare|bypass akamai|bypass datadome|bypass perimeterx|proxy rotation|account pool|ip pool|solve captcha|stealth recipe|behavioral mimicry|human-like mouse|trajectory generator|mouse movement generation to evade|VMP reconstruction|challenge solver|FLAG\\{|hook bypass|private training solution|apk modification|re-signing|root requirement|ssl pinning bypass|final submit by default" -Label "Android Pro forbidden recommendations" -Paths @("failure_doctor\android_pro", "templates\android_flows", "docs\ANDROID_PRODUCTION_HARDENING.md", "docs\ANDROID_SAFETY_BOUNDARY_v5.2.md", "docs\RELEASE_NOTES_v5.2.0.md", "README.md", "README.zh-CN.md", "validation")
Test-Pattern -Pattern "captcha bypass|anti-bot evasion|fingerprint spoofing|dynamic signature cracking|bypass cloudflare|bypass akamai|bypass datadome|bypass perimeterx|proxy rotation|account pool|ip pool|solve captcha|stealth recipe|behavioral mimicry|human-like mouse|trajectory generator|mouse movement generation to evade|VMP reconstruction|challenge solver|FLAG\\{|hook bypass|private training solution|apk modification|apk patch|re-signing|root requirement|ssl pinning bypass|real final submit|real business mutation|external screenshot upload|browser profile access|credential store access" -Label "Android Ops forbidden recommendations" -Paths @("failure_doctor\android_ops", "templates\android_business_flows", "templates\android_device_matrix", "examples\android_ops_cases", "docs\ANDROID_REAL_DEVICE_FARM.md", "docs\ANDROID_APPIUM_ORCHESTRATION.md", "docs\ANDROID_DEVICE_LEASE_AND_RECOVERY.md", "docs\ANDROID_BUSINESS_WORKFLOW_TEMPLATES.md", "docs\ANDROID_BUSINESS_DATA_BINDING.md", "docs\ANDROID_WORKFLOW_SCHEDULER.md", "docs\ANDROID_FLAKY_FLOW_DETECTION.md", "docs\ANDROID_COMPATIBILITY_REPORT.md", "docs\ANDROID_REAL_DEVICE_REPLAY.md", "docs\ANDROID_MUTATION_GUARD.md", "docs\ANDROID_OPS_DASHBOARD.md", "docs\ANDROID_PRODUCTION_RUNBOOK.md", "docs\RELEASE_NOTES_v5.3.0.md", "README.md", "README.zh-CN.md", "validation\android_ops_validation.json")
Test-Pattern -Pattern "captcha bypass|anti-bot evasion|fingerprint spoofing|dynamic signature cracking|bypass cloudflare|bypass akamai|bypass datadome|bypass perimeterx|proxy rotation|account pool|ip pool|solve captcha|stealth recipe|behavioral mimicry|human-like mouse|trajectory generator|mouse movement generation to evade|VMP reconstruction|challenge solver|FLAG\\{|hook bypass|private training solution|apk modification|apk patch|re-signing|root requirement|ssl pinning bypass|real final submit|real business mutation|external screenshot upload|browser profile access|credential store access" -Label "Android Mobile Stable forbidden recommendations" -Paths @("failure_doctor\android_authoring", "failure_doctor\android_pilot", "failure_doctor\android_dx", "failure_doctor\android_playbooks", "failure_doctor\android_real_pilot", "failure_doctor\android_lab", "failure_doctor\mobile_stability", "examples\android_authoring_cases", "examples\android_pilot_cases", "examples\android_dx_cases", "templates\android_acceptance_flows", "templates\android_assertions", "templates\android_business_packs", "templates\android_pilot_projects", "templates\android_playbooks", "docs\RELEASE_NOTES_v5.4.0.md", "docs\RELEASE_NOTES_v5.5.0.md", "docs\RELEASE_NOTES_v5.6.0.md", "docs\RELEASE_NOTES_v5.7.0.md", "docs\RELEASE_NOTES_v5.8.0.md", "docs\RELEASE_NOTES_v5.9.0.md", "docs\RELEASE_NOTES_v6.0.0.md", "README.md", "README.zh-CN.md", "validation\android_authoring_validation.json", "validation\android_pilot_validation.json", "validation\android_deep_diagnostics_validation.json", "validation\android_playbook_validation.json", "validation\real_apk_pilot_program_validation.json", "validation\android_device_lab_hardening_validation.json", "validation\mobile_automation_stability_validation.json")

# 6. Docs audit: check overclaim phrases
Test-Pattern-Docs -Pattern "auto.*scraper|auto.*crawler|production.*crawl|bypass.*captcha|evade.*anti" -Label "Overclaim in docs"

Write-Host ""
if ($Pass) {
    Write-Host "=== SAFETY SCAN: PASS ===" -ForegroundColor Green
} else {
    Write-Host "=== SAFETY SCAN: FAIL ===" -ForegroundColor Red
}
exit $(if ($Pass) { 0 } else { 1 })
