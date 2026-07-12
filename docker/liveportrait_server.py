#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# © 1993-2026 Abhishek Choudhary · AyeAI
"""TransEg avatar backend — audio-driven talking face, headless.

Runs INSIDE the FasterLivePortrait image (shaoguo/faster_liveportrait:v3), cwd
/root/FasterLivePortrait, so CUDA / TensorRT / onnxruntime-gpu stay in the container
(INTENT: Container Requirements). It is the SOLE GPU tenant.

Path (FLP's own audio-driven path, not an invention — see
src/pipelines/gradio_live_portrait_pipeline.py::run_audio_driving and api.py::run_with_pkl):
  audio.wav -> JoyVASAAudio2MotionPipeline.gen_motion_sequence() -> motion pickle
            -> FasterLivePortraitPipeline.run_with_pkl() frame loop -> mp4
            -> ffmpeg mux of the driving audio -> mp4 with sound

ORACLE: verified only on the target box (RTX 3050). Nothing here is claimed to pass
until scripts/avatar_smoke.sh writes a real mp4.
"""
import argparse, base64, json, os, subprocess, time, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import cv2, numpy as np
from omegaconf import OmegaConf
from src.pipelines.faster_live_portrait_pipeline import FasterLivePortraitPipeline
from src.pipelines.joyvasa_audio_to_motion_pipeline import JoyVASAAudio2MotionPipeline

ARGS = None
PIPE = None          # lazy: first render pays the model load; /health stays fast
JOYVASA = None
WORK = "/root/FasterLivePortrait/transeg_work"      # in-folder rule, never /tmp


def _cfg():
    cfg = OmegaConf.load(ARGS.cfg)
    cfg.infer_params.flag_pasteback = True           # full frame, not just the 512 crop
    return cfg


def _pipes():
    global PIPE, JOYVASA
    if PIPE is None:
        cfg = _cfg()
        PIPE = FasterLivePortraitPipeline(cfg=cfg, is_animal=False)   # human, not animal
        JOYVASA = JoyVASAAudio2MotionPipeline(
            motion_model_path=cfg.joyvasa_models.motion_model_path,
            audio_model_path=cfg.joyvasa_models.audio_model_path,
            motion_template_path=cfg.joyvasa_models.motion_template_path,
            cfg_mode=cfg.infer_params.cfg_mode,
            cfg_scale=cfg.infer_params.cfg_scale)
    return PIPE, JOYVASA


def render(audio_path, source_image_path, tag):
    pipe, joyvasa = _pipes()
    if not pipe.prepare_source(source_image_path, realtime=False):
        raise RuntimeError(f"no face found in source image {source_image_path}")

    motion = joyvasa.gen_motion_sequence(audio_path)          # audio -> LivePortrait motion
    fps = int(motion["output_fps"])
    h, w = pipe.src_imgs[0].shape[:2]
    silent = os.path.join(WORK, tag + "-silent.mp4")
    out_path = os.path.join(WORK, tag + ".mp4")

    vout = cv2.VideoWriter(silent, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    motion_lst = motion["motion"]
    c_eyes = motion.get("c_eyes_lst", motion.get("c_d_eyes_lst"))
    c_lip = motion.get("c_lip_lst", motion.get("c_d_lip_lst"))
    times = []
    for i in range(len(motion_lst)):
        t0 = time.time()
        _, out_org = pipe.run_with_pkl([motion_lst[i], c_eyes[i], c_lip[i]],
                                       pipe.src_imgs[0], pipe.src_infos[0],
                                       first_frame=(i == 0))
        if out_org is None:
            continue
        times.append(time.time() - t0)
        vout.write(cv2.cvtColor(out_org, cv2.COLOR_RGB2BGR))
    vout.release()

    subprocess.check_call(["ffmpeg", "-loglevel", "error", "-i", silent, "-i", audio_path,
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                           "-map", "0:v", "-map", "1:a", "-shortest", "-r", str(fps),
                           out_path, "-y"])
    os.remove(silent)
    med = float(np.median(times)) * 1000 if times else 0.0
    return out_path, fps, len(times), med


class H(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path != "/health":
            return self._json(404, {"error": "not found"})
        cfg = _cfg()
        ck = os.path.dirname(str(cfg.joyvasa_models.motion_model_path))
        self._json(200, {"service": "faster-liveportrait", "status": "ok",
                         "loaded": PIPE is not None, "cfg": ARGS.cfg,
                         "joyvasa_present": os.path.exists(ck), "device": "cuda"})

    def do_POST(self):
        if self.path != "/render":
            return self._json(404, {"error": "not found"})
        try:
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            tag = uuid.uuid4().hex[:12]
            os.makedirs(WORK, exist_ok=True)
            wav = os.path.join(WORK, tag + ".wav")
            with open(wav, "wb") as f:
                f.write(base64.b64decode(body["audio_b64"]))
            if body.get("source_image_b64"):
                src = os.path.join(WORK, tag + ".png")
                with open(src, "wb") as f:
                    f.write(base64.b64decode(body["source_image_b64"]))
            else:
                src = ARGS.source          # the stage-0 face artifact on disk
            mp4, fps, frames, ms = render(wav, src, tag)
            with open(mp4, "rb") as f:
                video = base64.b64encode(f.read()).decode()
            self._json(200, {"video_b64": video, "fps": fps, "frames": frames,
                             "median_ms_per_frame": round(ms, 2),
                             "engine": "faster-liveportrait+joyvasa"})
        except Exception as e:
            self._json(500, {"error": "%s: %s" % (type(e).__name__, e)})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8093)
    ap.add_argument("--cfg", default="configs/onnx_infer.yaml",
                    help="configs/trt_infer.yaml once all_onnx2trt.sh has run (faster)")
    ap.add_argument("--source", default="/models/liveportrait/source.png",
                    help="default stage-0 face artifact if the request carries none")
    ARGS = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    print("[transeg-avatar] serving on %s:%d cfg=%s" % (ARGS.host, ARGS.port, ARGS.cfg), flush=True)
    ThreadingHTTPServer((ARGS.host, ARGS.port), H).serve_forever()
