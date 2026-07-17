<!-- THIN OVERLAY — the MASTER CONTRACT at zistgah/governance/CONTRACT.md governs.
     This file only ADDS TransEg-specific constraints. It may never relax the master. -->
# CONTRACT — zistgah/transeg (Project TransEg core)

Any session — human or AI — **maintains contract and context**.

## Inherited (master, non-negotiable)
Sole author Abhishek Choudhary · affiliation **AyeAI only** · © 1993–2026 Abhishek Choudhary.
All rights reserved except per category: software `GPL-3.0-or-later` · content `CC-BY-SA-4.0`
· metadata `CC0-1.0` · novel methods proprietary (patents reserved). No fabrication — every
DOI referenced must be verified. Verify by execution; nothing ships on assertion. In-folder
rule (no /tmp). Contribution gate on every change.

## TransEg-specific additions
1. **Fully local by default.** No cloud, no telemetry, no hidden uploads. Any networking is
   explicit opt-in in `configs/transeg.yaml`. A service that phones home is a contract breach.
2. **Four typed layers, never conflated:** HumanIdentity → Representation → DigitalTwin →
   TransEg. Types, permissions, and lifecycle rules live in `zistgah/transeg-idgov`. Any code
   path that treats them as interchangeable is a defect.
3. **Component Based Engineering.** Every pipeline stage is a replaceable component behind a
   REST contract. No direct service-to-service coupling; the gateway composes.
4. **VRAM discipline (4 GB target):** avatar (FasterLivePortrait) is the sole GPU tenant.
   ASR, VAD, LLM, TTS run CPU by default. No duplicate model loading.
5. **LLM is a capability contract, not a model name.** Discovery + preference order in
   `configs/transeg.yaml`; user configuration always wins.
6. **INTENT.md is verbatim and append-only.** The painting's ground truth is never rewritten.
7. **Identity data is the owner's.** Export, deletion, backup, encryption are load-bearing;
   a release that breaks any of them does not ship.
8. **Staggered Upload gating:** no stage may implicitly grant capabilities from any other
   stage. Each stage is independently enabled, revoked, versioned, and auditable.
9. **Mock oracles are labelled.** In-container CI verifies API contracts and the pipeline in
   mock mode. Model-dependent claims are verified only by `bootstrap.sh --validate` on the
   target machine. Never report a mock pass as a hardware pass.
10. **DOI/publishing:** misty-doi + OpenTimestamps; DOI token `10.5281/zenodo.21321558` injected
    post-mint via the seed script. `isDerivedFrom` → PEDLER doi:10.5281/zenodo.17497559
    (verified by direct read 2026-06-29; resolve-check before mint). No other related
    identifiers unless verified.
