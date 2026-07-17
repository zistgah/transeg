# QUESTS — VGC stage ledger for zistgah/transeg v0.1.0
_AAB discipline: a quest completes only with a recorded oracle and typed evidence.
Grounding rule: no oracle, no glow._

| Quest | Deliverable | Oracle | Evidence (typed) | State |
|---|---|---|---|---|
| Q0 Contract & Context | INTENT.md verbatim + dated appendix; CONTRACT/CONTEXT thin overlays; NOTICE; LICENSE | O-GATE `--check` | execution log, this session 2026-07-12T06:57:17Z: gate PASSED | ✅ verified |
| Q1 Skeleton | spec layout + compose (11 services) | O-COMPOSE | yaml load + sole-GPU-tenant assert: "compose OK · 11 services · sole GPU tenant: faster-liveportrait" | ✅ verified |
| Q2 Gateway + health mesh | FastAPI gateway, 7 components, aggregate /health | O-CI test_health_mesh | pytest: every component "ok" | ✅ verified |
| Q3 Identity graph | memory service: typed nodes (provenance/timestamps/confidence/permissions), edges, export/delete, encrypted backup/restore | O-CI test_identity_graph | pytest: roundtrips incl. wrong-key rejection; provenance + layer enforcement (422) | ✅ verified |
| Q4 Staggered Upload | typed stage machine 0-7 | O-CI test_staggered_upload | pytest: no implicit grants; independent revoke; version+audit per mutation | ✅ verified |
| Q5 Component adapters | vad/asr/llm/tts/avatar adapters, mock+real modes; LLM capability contract | O-CI test_pipeline_mock (mock tier) | pytest: full composed flow, gates enforced, preference-order resolution | ✅ verified (mock) / ⬜ on-target |
| Q6 Bootstrap + pins | bootstrap.sh (dry-run/validate/models/pin/full) | bash -n + dry-run here; O-TARGET on your machine | dry-run plan captured; **hardware claims remain unverified until O-TARGET** | ◐ dry-run only |
| Q7 Publish rail | misty.json, CITATION.cff, seed.json, seed script, provenance/ | O-GATE; misty validate + mint = author's machine | json/cff validated; DOI token 10.5281/zenodo.21321558; isDerivedFrom PEDLER 10.5281/zenodo.17497559 | ◐ pre-mint |
| Q-PROV Concept provenance | TransEg decades-old archival evidence (hindawi.in, Wayback) | author retrieval | **Declared** (author testimony). Upgrade to Verified: `curl "http://web.archive.org/cdx/search/cdx?url=hindawi.in*&output=text&limit=2000" \| grep -i transeg` — then commit the snapshot URL here + OTS-stamp it | ⬜ declared |

## Author's push checklist (the steps the AI never runs)
1. `scripts/zistgah_seed_transeg.sh --check` → expect gate PASSED.
2. Resolve-check PEDLER before mint: `curl -sIL https://doi.org/10.5281/zenodo.17497559 | head -1` → 200.
3. `--push` (gh auth) → repo live under zistgah.
4. Patch zistgah/governance REGISTRY.json known_dois with the PEDLER DOI (seed.json → registry_patch).
5. Mint via misty/mistyx on your machine → `--inject-doi <real doi>` → commit → `--ots`.
6. On target: `scripts/bootstrap.sh` → ALL COMPONENTS HEALTHY flips Q6 + Q5-on-target to ✅.
7. Q-PROV: run the CDX query, commit the snapshot URL, OTS-stamp.
