#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
# Repairs the TransEg core repo: injects the LIVE published DOI, fixes the
# truncated "10.5281/zenodo.21321558" in README, corrects CITATION.cff type. Verify-by-execution.
set -euo pipefail
DOI="10.5281/zenodo.21321558"          # the published version DOI
CONCEPT="10.5281/zenodo.21321557"      # the all-versions concept DOI
PEDLER="10.5281/zenodo.17497559"       # the parent (must never be overwritten)
cd "${1:-.}"
ok(){ printf '  \033[32m✓\033[0m %s\n' "$*"; }

# 1. repair any truncated DOI first (10.5281/zenodo.21321558 with no digits), but NEVER touch PEDLER
grep -rlI "10\.5281/zenodo\.\([^0-9]\|$\)" . --exclude-dir=.git 2>/dev/null | while read -r f; do
  # replace a bare 'zenodo.' (not followed by a digit) with the real version DOI
  perl -0pi -e 's{10\.5281/zenodo\.(?![0-9])}{10.5281/zenodo.21321558}g' "$f"
  ok "repaired truncated DOI in $f"
done

# 2. inject the placeholder token everywhere it still lives
grep -rlI "10.5281/zenodo.21321558" . --exclude-dir=.git 2>/dev/null | while read -r f; do
  sed -i "s|10.5281/zenodo.21321558|$DOI|g" "$f"; ok "injected DOI -> $f"
done

# 3. CITATION.cff: fix identifier type other->doi, ensure both DOIs present
if [ -f CITATION.cff ]; then
  python3 - "$DOI" "$CONCEPT" <<'PY'
import sys
try: import yaml
except ImportError: sys.exit(0)
doi,concept=sys.argv[1],sys.argv[2]
d=yaml.safe_load(open("CITATION.cff"))
ids=d.setdefault("identifiers",[])
for i in ids:
    if i.get("value",'').startswith("10.5281/zenodo.21321558") and i.get("type")=="other":
        i["type"]="doi"
have={i.get("value") for i in ids}
if doi not in have: ids.append({"type":"doi","value":doi,"description":"Version DOI (v0.1.0)"})
if concept not in have: ids.append({"type":"doi","value":concept,"description":"Concept DOI (all versions)"})
d["doi"]=concept
yaml.safe_dump(d,open("CITATION.cff","w"),sort_keys=False,allow_unicode=True)
print("  \033[32m✓\033[0m CITATION.cff: types fixed, version+concept DOIs present")
PY
fi

# 4. VERIFY — no placeholder, no truncated DOI, PEDLER intact
echo "  --- verification ---"
! grep -rI "10.5281/zenodo.21321558" . --exclude-dir=.git >/dev/null 2>&1 && ok "no placeholders remain" || { echo "  ✗ placeholder survives"; exit 1; }
! grep -rI "10\.5281/zenodo\.\([^0-9]\|$\)" . --exclude-dir=.git >/dev/null 2>&1 && ok "no truncated DOIs" || { echo "  ✗ truncated DOI survives"; exit 1; }
grep -rI "$PEDLER" . --exclude-dir=.git >/dev/null 2>&1 && ok "PEDLER lineage intact ($PEDLER)" || echo "  ! PEDLER not found (check isDerivedFrom)"
echo "  DOIs now present:"; grep -rhoI "10\.5281/zenodo\.[0-9]*" . --exclude-dir=.git | sort | uniq -c | sed 's/^/    /'
echo
echo "  Review, then: git add -A && git commit -m 'DOI $DOI (v0.1.0)' && git push"
echo "  (do NOT commit zistgah_mint.sh itself — add it to .gitignore or rm it)"
