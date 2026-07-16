$compilerPath = Join-Path $PSScriptRoot "compiler"

if (-not (Test-Path $compilerPath)) {
    Write-Host "compiler directory not found at $compilerPath"
    exit 1
}

$files = Get-ChildItem -Path $compilerPath -Recurse -Filter "*.toon" | Sort-Object FullName

$totalLines = 0
$totalWords = 0
$totalChars = 0
$totalTokens = 0

Write-Host "`n=== TOKEN COUNT REPORT ==="
Write-Host ("{0,-55} {1,7} {2,7} {3,8} {4,10}" -f "File", "Lines", "Words", "Chars", "Est.Tokens")
Write-Host ("-" * 90)

foreach ($f in $files) {
    $content = Get-Content -Path $f.FullName -Raw
    $lines = ($content -split "`r`n|`n").Length
    $words = $content.Split(@(" ","`t","`r","`n"), [System.StringSplitOptions]::RemoveEmptyEntries).Length
    $chars = $content.Length
    $estTokens = [math]::Round($words * 1.33)

    $relPath = $f.FullName.Substring($PSScriptRoot.Length + 1)

    Write-Host ("{0,-55} {1,7} {2,7} {3,8} {4,10}" -f $relPath, $lines, $words, $chars, $estTokens)

    $totalLines += $lines
    $totalWords += $words
    $totalChars += $chars
    $totalTokens += $estTokens
}

Write-Host ("-" * 90)
Write-Host ("{0,-55} {1,7} {2,7} {3,8} {4,10}" -f "TOTAL ($($files.Count) files)", $totalLines, $totalWords, $totalChars, $totalTokens)
Write-Host "`n* Token estimate: words x 1.33 (rough approximation)"
Write-Host "  For precise count, use: pip install tiktoken && python -c `"import tiktoken; enc = tiktoken.get_encoding('cl100k_base'); ...`""
