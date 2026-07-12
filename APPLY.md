# Applying this patch to your clone of zistgah/transeg

```bash
cd ~/work/12jul/transeg-0.1.0/transeg          # or a fresh: gh repo clone zistgah/transeg
tar xzf transeg-avatar-patch.tar.gz --strip-components=1   # overwrites 5 files, adds 5

git add -A && git commit -m "avatar: real JoyVASA audio-driven backend; vad: silero in-process; compose: upstream FLP image, publish staggered port (D1-D4)"
git push

scripts/zistgah_seed_transeg.sh --check        # gate must still say PASSED
python3 -m pytest tests -q                     # 10/10 must still be green
```

Files: `docker/liveportrait_server.py` (rewritten), `services/vad/app.py` (rewritten),
`compose/docker-compose.yml` (rewritten), `docker/vad.Dockerfile` (new),
`scripts/avatar_setup.sh` (new), `scripts/avatar_smoke.sh` (new), `docs/avatar.md` (new),
`DEFECTS.md` (new). Delete the now-unused `docker/liveportrait.Dockerfile`.
