# Threat model (v0.1)
<!-- content CC-BY-SA-4.0 -->
Assets: the identity graph (highest value — it is the person's representation), the
staggered-upload state, model weights, release artifacts. Adversaries considered:
exfiltration (any process shipping identity data off-machine), impersonation (unauthorized
construction or use of the twin), tampering (silent mutation of memories — an integrity
attack on identity), and supply chain (poisoned images/models). Mitigations in v0.1: fully
local default with networking opt-in; the four-layer type system and stage gates limit what
any caller can reach; every memory mutation carries provenance and timestamps (traceable
memory); encrypted owner-held backups (the key is returned to the owner, never stored);
image digest pinning via bootstrap --pin; release checksums + OpenTimestamps via the seed
script. Known gaps, tracked for v0.2: per-node signatures (idgov signature envelope exists,
enforcement is not yet wired into the memory service), at-rest database encryption,
mutual-auth between containers on the compose network, and reproducible container builds.
Do not expose the compose network beyond localhost until those land.
