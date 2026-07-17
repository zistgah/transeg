# MINT RUNBOOK — TransEg v0.1.0 (three DOIs)
© 1993–2026 Abhishek Choudhary · AyeAI · **You run every command. I mint nothing.**

Every flag below was read off `misty --help` (misty-doi 1.0.1, installed from PyPI and
exercised), not from memory. Every metadata file below was put through `misty validate`
and `misty transform`, and the generated `build/zenodo.json` was inspected.

---

## What I found and fixed before you minted

| | Problem | Consequence if minted as-is | Fixed |
|---|---|---|---|
| **M1** | `version` was absent from misty.json → misty's canonical schema filled its template default | Zenodo record would read **v1.0.0** for software you call v0.1.0. Immutable once published. | `"version": "0.1.0"` added to all three |
| **M2** | `misty transform` **drops `publication_date`** — it is not in the emitted zenodo.json | Zenodo stamps *today*. Today is 2026-07-12, which is the date you want — **so this is harmless only if you mint today**. Mint later → wrong date. | field kept; mint today, or set the date in the Zenodo UI before publishing |
| **M3** | `repository` field (misty template has it) was missing | record with no link back to source | GitHub URL added to all three |
| **M4** | `license: gpl-3.0-or-later` — valid SPDX, but Zenodo's legacy vocabulary sometimes wants `gpl-3.0` | HTTP 400 at deposit, or a wrong licence on the record | **unresolved from here — this is what `--sandbox` is for.** If sandbox 400s on licence, change to `gpl-3.0` and re-run sandbox. |

---

## The protocol — sandbox, then draft, then publish

```bash
export ZENODO_TOKEN=$(cat ~/Documents/zenodo_token_20260612)
export PATH="$HOME/.local/bin:$PATH"

cd ~/work/12jul/transeg-0.1.0/transeg
git pull                                    # take the corrected misty.json

# 0. PRE-FLIGHT — the lineage DOI must actually resolve before you cite it
curl -sIL https://doi.org/10.5281/zenodo.17497559 | head -1     # expect 200/30x -> zenodo
scripts/zistgah_seed_transeg.sh --check                          # gate PASSED
scripts/test.sh                                                  # 10/10 (hermetic venv)

# 1. build the artefact you are actually depositing (source tarball of the tagged tree)
git archive --format=tar.gz --prefix=transeg-0.1.0/ -o transeg-0.1.0.tar.gz HEAD
sha256sum transeg-0.1.0.tar.gz | tee provenance/release.sha256

# 2. SANDBOX first. Costs nothing, proves the payload, catches M4.
misty publish -m misty.json -f transeg-0.1.0.tar.gz --sandbox
#    -> open the sandbox record. Check: title, version 0.1.0, licence, ORCID,
#       affiliation "AyeAI, Hyderabad, India", related identifier isDerivedFrom PEDLER.

# 3. REAL Zenodo, but as a DRAFT — nothing public, nothing immutable yet
misty publish -m misty.json -f transeg-0.1.0.tar.gz --no-publish
#    -> open the draft on zenodo.org. Read every field again. THIS is the last exit.

# 4. Publish. IRREVERSIBLE. The DOI is minted the moment you do this.
misty publish -m misty.json -f transeg-0.1.0.tar.gz

# 5. Inject the real DOI back into the repo, seal, push
scripts/zistgah_seed_transeg.sh --inject-doi 10.5281/zenodo.21321558NNNNNNNN
scripts/zistgah_seed_transeg.sh --ots
git add -A && git commit -m "DOI 10.5281/zenodo.21321558NNNNNNNN (v0.1.0)" && git push
```

Then the same five steps in `transeg-idgov` and `transeg-research` (their seed scripts have
the same `--inject-doi` / `--ots` modes).

## Registry
After the three DOIs exist, patch `zistgah/governance` `REGISTRY.json` `known_dois` with
**four** entries: the three new ones **plus PEDLER `10.5281/zenodo.17497559`**, which is
still missing from the registry (that gap is why `seed.json` carries a `registry_patch`).
Until PEDLER is in `known_dois`, any repo citing it fails a strict gate.

## Concept DOI
`misty publish` mints a fresh record. For the *concept* DOI chain (so v0.2 supersedes v0.1
rather than orphaning it), use `mistyx newversion` on the next release — that is exactly the
gap it was written to close. Do **not** mint three fresh records for v0.2.

## What I did not verify
Zenodo is unreachable from my sandbox. I never touched your token. Sandbox → draft →
publish is the whole safety net; do not skip a rung because the first two looked fine.
