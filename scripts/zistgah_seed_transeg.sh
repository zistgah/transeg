#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
# Gated seed for zistgah/transeg — zseed pattern; in-folder only; author pushes, AI never does.
#   --check        preflight only (default)
#   --push         create/push zistgah/transeg via gh (requires your auth)
#   --inject-doi D replace ZENODO-DOI-PENDING with the real minted DOI, post-mint
#   --ots          OpenTimestamps-stamp the release tarball hash into provenance/
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"; cd "$HERE"
MODE="${1:---check}"
log(){ printf '[seed] %s\n' "$*"; }
gate(){
  X=(--exclude-dir=.git --exclude="zistgah_seed_transeg.sh")   # never scan this gate itself
  log "gate: contract/context/intent present"
  for f in CONTRACT.md CONTEXT.md INTENT.md NOTICE LICENSE CITATION.cff misty.json seed.json QUESTS.md aab/manifest.json; do
    [ -f "$f" ] || { echo "MISSING $f"; exit 1; }
  done
  log "gate: no forbidden credits"
  ! grep -RIni "${X[@]}" -e "srija" -e "katta" . || { echo "FORBIDDEN NAME FOUND"; exit 1; }
  log "gate: affiliation discipline (AyeAI only)"
  ! grep -RIn "${X[@]}" "Independent Researcher" . || { echo "BAD AFFILIATION"; exit 1; }
  log "gate: DOI discipline — only verified DOIs"
  ALLOWED="10.5281/zenodo.17497559"
  FOUND=$(grep -RhoI "${X[@]}" "10\.5281/zenodo\.[0-9]*" . | sort -u)
  for d in $FOUND; do case " $ALLOWED " in *" $d "*) ;; *) echo "UNVERIFIED DOI $d"; exit 1;; esac; done
  log "gate: pre-mint resolve check reminder"
  log "  run on your machine: curl -sIL https://doi.org/10.5281/zenodo.17497559 | head -1  (expect 200)"
  log "gate: PASSED"
}
case "$MODE" in
  --check) gate ;;
  --push)
    gate
    command -v gh >/dev/null || { echo "gh CLI required"; exit 1; }
    git init -q 2>/dev/null || true
    git add -A && git commit -q -m "TransEg v0.1.0 — local digital twin reference implementation" || true
    git branch -M main
    gh repo view zistgah/transeg >/dev/null 2>&1 \
      && { git remote add origin "$(gh repo view zistgah/transeg --json url -q .url).git" 2>/dev/null || true; git push -u origin main; } \
      || gh repo create zistgah/transeg --public --source=. --push \
           --description "Project TransEg — local digital twin reference implementation (identity continuity research platform)"
    log "REGISTRY PATCH: add PEDLER DOI to zistgah/governance REGISTRY.json known_dois (see seed.json registry_patch)"
    ;;
  --inject-doi)
    DOI="${2:?usage: --inject-doi 10.5281/zenodo.NNNNN}"
    grep -rl "ZENODO-DOI-PENDING" README.md CITATION.cff 2>/dev/null | while read -r f; do
      sed -i "s|ZENODO-DOI-PENDING|$DOI|g" "$f"; log "injected $DOI -> $f"
    done ;;
  --ots)
    command -v ots >/dev/null || { echo "opentimestamps-client required"; exit 1; }
    T="transeg-0.1.0.tar.gz"; tar czf "$T" --exclude=.git --exclude="$T" .
    sha256sum "$T" | tee provenance/release.sha256
    ots stamp provenance/release.sha256 && log "OTS proof -> provenance/release.sha256.ots" ;;
  *) echo "unknown mode $MODE"; exit 1 ;;
esac
