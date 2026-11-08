#!/usr/bin/env python3
"""v0.8.9.3 source and migration contract; no live Jellyfin guarantees."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
project = root / "src/Jellyfin.Plugin.FranchiseExplorer"
cs = (project / "Web/HomeTileRegistrationService.cs").read_text(encoding="utf-8")
js = (project / "Web/franchise-my-media.js").read_text(encoding="utf-8")
version = (project / "Jellyfin.Plugin.FranchiseExplorer.csproj").read_text(encoding="utf-8")
readme = (root.parent / "README.md").read_text(encoding="utf-8")

for field in ("Version", "AssemblyVersion", "FileVersion"):
    assert f"<{field}>0.8.9.26</{field}>" in version, field
assert 'CurrentScriptId = "jellyfin-franchise-explorer-my-media-v08926"' in cs
assert '"jellyfin-franchise-explorer-my-media-v08925-menu3",' in cs
assert '"jellyfin-franchise-explorer-my-media-v08925",' in cs
assert '"jellyfin-franchise-explorer-my-media-v08923-menu3",' in cs
assert '"jellyfin-franchise-explorer-my-media-v08923",' in cs
assert 'Franchise Explorer 0.8.9.26 loaded' in cs
assert js.index('if (window.__franchiseExplorerMyMediaTileLoaded) return;') < js.index("window.__franchiseExplorerUiBuild = 'menu3'")
assert '"jellyfin-franchise-explorer-my-media-v08914"' in cs
assert '"jellyfin-franchise-explorer-my-media-v08913"' in cs
assert '"jellyfin-franchise-explorer-my-media-v0899"' in cs
assert '"jellyfin-franchise-explorer-my-media-v0894"' in cs
assert '"jellyfin-franchise-explorer-my-media-v0893"' in cs
assert '"jellyfin-franchise-explorer-my-media-v1"' in cs
assert '["id"] = CurrentScriptId' in cs
assert '["pluginVersion"] = "0.8.9.26"' in cs
assert 'GetMethod("UnregisterScript"' in cs
assert cs.index('register.Invoke(null, new[] { payload })') < cs.index('unregister.Invoke(')
assert 'if (result is not bool success || !success) return false;' in cs
assert 'data-fe-version' in js and '__franchiseExplorerUiVersion' in js
assert "CACHE_PREFIX = 'fe-franchise-home-v08926:'" in js
assert 'confirmedEmpty = active.length === 0' in js
assert 'Loading your franchise watch orders' in js
assert 'Franchise Explorer Settings' in js
assert 'openBrowse' not in js
assert 'actionSheetMenuItem' in js
assert 'console.warn(' in js and 'error?.message' in js
assert 'https://raw.githubusercontent.com/skriewel/jellyfin-plugins/main/manifest.json' in readme
assert 'https://raw.githubusercontent.com/n00bcodr/jellyfin-plugins/main/manifest.json' in readme
assert 'jellyfin-franchise-explorer-my-media-v08926' in readme
assert 'docs/Gost1o1-logo.png' in readme
print('v0.8.9.3 version, script migration, home persistence, and README contracts passed.')
