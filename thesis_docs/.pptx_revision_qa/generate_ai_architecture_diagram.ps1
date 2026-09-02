param(
    [string]$OutputPath = (Join-Path $PSScriptRoot '..\assets\AI_Model_Architecture_Diagram.svg'),
    [switch]$SkipPng
)

$ErrorActionPreference = 'Stop'

$resolvedOutput = [System.IO.Path]::GetFullPath($OutputPath)
$outputDirectory = Split-Path -Parent $resolvedOutput
New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null

$svg = @'
<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" viewBox="0 0 1600 900" role="img" aria-labelledby="diagram-title diagram-desc">
  <title id="diagram-title">AI model architecture for contextual and trajectory-based conversation review</title>
  <desc id="diagram-desc">A left-to-right pipeline. The current turn and up to two preceding turns enter a context-conditioned DistilBERT classifier. Its contextual author-derived proxy score becomes part of seven chronological trajectory features. A primary LSTM models the sequence and a frozen threshold prioritizes conversations for human review. A lower band lists the seven features and the experiment controls.</desc>
  <defs>
    <marker id="arrowhead" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto" markerUnits="strokeWidth">
      <path d="M 0 0 L 12 6 L 0 12 z" fill="#5B6F82"/>
    </marker>
    <filter id="shadow" x="-10%" y="-15%" width="120%" height="140%">
      <feDropShadow dx="0" dy="3" stdDeviation="4" flood-color="#17324D" flood-opacity="0.12"/>
    </filter>
    <style>
      .title { font: 700 42px 'Aptos Display', 'Segoe UI', Arial, sans-serif; fill: #17324D; }
      .subtitle { font: 400 21px 'Aptos', 'Segoe UI', Arial, sans-serif; fill: #516274; }
      .step { font: 700 15px 'Aptos', 'Segoe UI', Arial, sans-serif; letter-spacing: 1.5px; fill: #6A7886; }
      .node-title { font: 700 26px 'Aptos Display', 'Segoe UI', Arial, sans-serif; fill: #17324D; }
      .node-body { font: 400 20px 'Aptos', 'Segoe UI', Arial, sans-serif; fill: #31465A; }
      .section-title { font: 700 22px 'Aptos Display', 'Segoe UI', Arial, sans-serif; fill: #17324D; }
      .feature-title { font: 700 18px 'Aptos', 'Segoe UI', Arial, sans-serif; fill: #17324D; }
      .feature-body { font: 400 15px 'Aptos', 'Segoe UI', Arial, sans-serif; fill: #516274; }
      .control-title { font: 700 18px 'Aptos', 'Segoe UI', Arial, sans-serif; fill: #17324D; }
      .control-body { font: 500 17px 'Aptos', 'Segoe UI', Arial, sans-serif; fill: #31465A; }
      .footer { font: 500 18px 'Aptos', 'Segoe UI', Arial, sans-serif; fill: #31465A; }
      .node { stroke: #9AAABA; stroke-width: 1.5; filter: url(#shadow); }
      .feature { fill: #FFFFFF; stroke: #CBD5DF; stroke-width: 1.25; }
      .arrow { stroke: #5B6F82; stroke-width: 3; fill: none; marker-end: url(#arrowhead); }
    </style>
  </defs>

  <rect width="1600" height="900" fill="#FFFFFF"/>
  <rect x="56" y="54" width="8" height="74" rx="4" fill="#D6A327"/>
  <text x="86" y="88" class="title">AI Model Architecture</text>
  <text x="87" y="123" class="subtitle">Contextual turn analysis followed by chronological conversation modeling</text>

  <path class="arrow" d="M 300 275 H 326"/>
  <path class="arrow" d="M 546 275 H 572"/>
  <path class="arrow" d="M 762 275 H 788"/>
  <path class="arrow" d="M 1018 275 H 1044"/>
  <path class="arrow" d="M 1254 275 H 1280"/>

  <g aria-label="Step 1 context window">
    <text x="90" y="175" class="step">STEP 1</text>
    <rect class="node" x="90" y="190" width="210" height="170" rx="18" fill="#F5F7FA"/>
    <text x="195" y="238" text-anchor="middle" class="node-title">Context window</text>
    <text x="195" y="279" text-anchor="middle" class="node-body">
      <tspan x="195" dy="0">Current turn</tspan>
      <tspan x="195" dy="29">+ up to 2 prior turns</tspan>
    </text>
  </g>

  <g aria-label="Step 2 Layer 1 classifier">
    <text x="326" y="175" class="step">STEP 2</text>
    <rect class="node" x="326" y="190" width="220" height="170" rx="18" fill="#EAF2FA"/>
    <text x="436" y="232" text-anchor="middle" class="node-title">Layer 1</text>
    <text x="436" y="271" text-anchor="middle" class="node-body">
      <tspan x="436" dy="0">Context-conditioned</tspan>
      <tspan x="436" dy="29">DistilBERT classifier</tspan>
    </text>
  </g>

  <g aria-label="Step 3 contextual proxy score">
    <text x="572" y="175" class="step">STEP 3</text>
    <rect class="node" x="572" y="190" width="190" height="170" rx="18" fill="#F5F7FA"/>
    <text x="667" y="232" text-anchor="middle" class="node-title">Turn signal R<tspan baseline-shift="sub" font-size="18">t</tspan></text>
    <text x="667" y="271" text-anchor="middle" class="node-body">
      <tspan x="667" dy="0">Author-derived</tspan>
      <tspan x="667" dy="29">contextual proxy</tspan>
    </text>
  </g>

  <g aria-label="Step 4 seven trajectory features">
    <text x="788" y="175" class="step">STEP 4</text>
    <rect class="node" x="788" y="190" width="230" height="170" rx="18" fill="#EDF7F7"/>
    <text x="903" y="232" text-anchor="middle" class="node-title">Seven-feature</text>
    <text x="903" y="263" text-anchor="middle" class="node-title">trajectory</text>
    <text x="903" y="309" text-anchor="middle" class="node-body">Ordered at every turn</text>
  </g>

  <g aria-label="Step 5 Layer 2 LSTM">
    <text x="1044" y="175" class="step">STEP 5</text>
    <rect class="node" x="1044" y="190" width="210" height="170" rx="18" fill="#EAF5ED"/>
    <text x="1149" y="232" text-anchor="middle" class="node-title">Layer 2</text>
    <text x="1149" y="271" text-anchor="middle" class="node-body">
      <tspan x="1149" dy="0">Primary LSTM</tspan>
      <tspan x="1149" dy="29">sequence model</tspan>
    </text>
  </g>

  <g aria-label="Step 6 decision support">
    <text x="1280" y="175" class="step">STEP 6</text>
    <rect class="node" x="1280" y="190" width="240" height="170" rx="18" fill="#FFF3D6" stroke="#D6A327"/>
    <text x="1400" y="232" text-anchor="middle" class="node-title">Decision support</text>
    <text x="1400" y="271" text-anchor="middle" class="node-body">
      <tspan x="1400" dy="0">Frozen threshold</tspan>
      <tspan x="1400" dy="29">Human review priority</tspan>
    </text>
  </g>

  <rect x="56" y="406" width="1488" height="256" rx="18" fill="#F7F9FB"/>
  <text x="82" y="442" class="section-title">Seven chronological features at each turn</text>

  <g aria-label="Peak proxy score">
    <rect class="feature" x="82" y="463" width="330" height="76" rx="12"/>
    <text x="101" y="491" class="feature-title">1  Peak proxy score</text>
    <text x="101" y="518" class="feature-body">Highest R<tspan baseline-shift="sub" font-size="12">i</tspan> observed so far</text>
  </g>
  <g aria-label="Current proxy score">
    <rect class="feature" x="450" y="463" width="330" height="76" rx="12"/>
    <text x="469" y="491" class="feature-title">2  Current proxy score</text>
    <text x="469" y="518" class="feature-body">Current Layer 1 signal R<tspan baseline-shift="sub" font-size="12">t</tspan></text>
  </g>
  <g aria-label="Spike count">
    <rect class="feature" x="818" y="463" width="330" height="76" rx="12"/>
    <text x="837" y="491" class="feature-title">3  Spike count</text>
    <text x="837" y="518" class="feature-body">Scores above the frozen spike threshold</text>
  </g>
  <g aria-label="Spike then drop">
    <rect class="feature" x="1186" y="463" width="330" height="76" rx="12"/>
    <text x="1205" y="491" class="feature-title">4  Spike-then-drop</text>
    <text x="1205" y="518" class="feature-body">Persistent flag after a qualifying drop</text>
  </g>
  <g aria-label="Rate of change">
    <rect class="feature" x="266" y="559" width="330" height="76" rx="12"/>
    <text x="285" y="587" class="feature-title">5  Rate of change</text>
    <text x="285" y="614" class="feature-body">R<tspan baseline-shift="sub" font-size="12">t</tspan> - R<tspan baseline-shift="sub" font-size="12">t-1</tspan></text>
  </g>
  <g aria-label="Topic distance">
    <rect class="feature" x="634" y="559" width="330" height="76" rx="12"/>
    <text x="653" y="587" class="feature-title">6  Topic distance</text>
    <text x="653" y="614" class="feature-body">From a training-only benign centroid</text>
  </g>
  <g aria-label="Turn taking imbalance">
    <rect class="feature" x="1002" y="559" width="330" height="76" rx="12"/>
    <text x="1021" y="587" class="feature-title">7  Turn-taking imbalance</text>
    <text x="1021" y="614" class="feature-body">Cumulative difference in speaker turns</text>
  </g>

  <rect x="56" y="692" width="1488" height="112" rx="18" fill="#F5F7FA" stroke="#CBD5DF" stroke-width="1.25"/>
  <text x="82" y="724" class="control-title">Evaluation controls</text>
  <text x="82" y="762" class="control-body">Connected-author split</text>
  <text x="355" y="762" class="control-body" fill="#6A7886">&#8594;</text>
  <text x="395" y="762" class="control-body">Training-only resources</text>
  <text x="682" y="762" class="control-body" fill="#6A7886">&#8594;</text>
  <text x="722" y="762" class="control-body">Validation-only selection</text>
  <text x="1019" y="762" class="control-body" fill="#6A7886">&#8594;</text>
  <text x="1059" y="762" class="control-body">One-time held-out final test</text>

  <circle cx="67" cy="851" r="7" fill="#D6A327"/>
  <text x="87" y="858" class="footer">Output is a conversation-level review priority, not an autonomous enforcement decision.</text>
</svg>
'@

[System.IO.File]::WriteAllText($resolvedOutput, $svg, [System.Text.UTF8Encoding]::new($false))

$result = [ordered]@{
    svg = [ordered]@{
        output = $resolvedOutput
        width = 1600
        height = 900
        sha256 = (Get-FileHash -LiteralPath $resolvedOutput -Algorithm SHA256).Hash
    }
}

if (-not $SkipPng) {
    $edgeCandidates = @(
        'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        'C:\Program Files\Microsoft\Edge\Application\msedge.exe'
    )
    $edge = $edgeCandidates | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
    if (-not $edge) {
        throw 'Microsoft Edge was not found. Re-run with -SkipPng to generate only the SVG.'
    }

    $pngPath = [System.IO.Path]::ChangeExtension($resolvedOutput, '.png')
    $svgUri = [System.Uri]::new($resolvedOutput).AbsoluteUri
    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    & $edge '--headless' '--disable-gpu' '--hide-scrollbars' '--window-size=1600,900' "--screenshot=$pngPath" $svgUri 2>$null | Out-Null
    $edgeExitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousPreference

    if ($edgeExitCode -ne 0 -or -not (Test-Path -LiteralPath $pngPath)) {
        throw "PNG export failed with Edge exit code $edgeExitCode."
    }

    $result.png = [ordered]@{
        output = $pngPath
        width = 1600
        height = 900
        sha256 = (Get-FileHash -LiteralPath $pngPath -Algorithm SHA256).Hash
    }
}

$result | ConvertTo-Json -Depth 4
