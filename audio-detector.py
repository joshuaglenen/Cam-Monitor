#!/usr/bin/env python3
import os, sys, subprocess, numpy as np, time, datetime

RTSP = os.environ.get("RTSP_URL", "rtsp://joshglenen:joshglenen@192.168.2.247:554/stream2")
AR   = int(os.environ.get("AR", "16000"))        # sample rate
CHUNK_MS = int(os.environ.get("CHUNK_MS", "250"))# analysis window
RMS_DB  = float(os.environ.get("RMS_DB", "-25")) # overall loudness threshold (dBFS)
BARK_DB = float(os.environ.get("BARK_DB", "-30"))# 500–2000 Hz band
CRY_DB  = float(os.environ.get("CRY_DB", "-32")) # 300–800 Hz band
COOLDOWN = float(os.environ.get("COOLDOWN", "3"))

samples_per = AR * CHUNK_MS // 1000
fmt = np.int16
last_print = 0.0

def dbfs(x):
    # RMS in dBFS for int16
    rms = np.sqrt(np.mean((x.astype(np.float32)/32768.0)**2) + 1e-12)
    return 20*np.log10(rms + 1e-12)

def band_dbfs(x, low, high, sr):
    # quick FFT band power in dBFS
    n = len(x)
    win = np.hanning(n).astype(np.float32)
    X = np.fft.rfft((x.astype(np.float32)/32768.0)*win)
    freqs = np.fft.rfftfreq(n, 1/sr)
    band = (freqs >= low) & (freqs <= high)
    pwr = np.mean(np.abs(X[band])**2) + 1e-15
    return 10*np.log10(pwr)

def note(msg):
    global last_print
    now = time.time()
    if now - last_print >= COOLDOWN:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] {msg}", flush=True)
        last_print = now

cmd = [
    "ffmpeg", "-hide_banner", "-loglevel", "error",
    "-rtsp_transport", "tcp", "-i", RTSP,
    "-vn",           # no video
    "-ac", "1",      # mono
    "-ar", str(AR),  # sample rate
    "-f", "s16le", "-"  # raw PCM to stdout
]

proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=0)

buf = b""
bytes_per = samples_per * np.dtype(fmt).itemsize

try:
    while True:
        chunk = proc.stdout.read(bytes_per - len(buf))
        if not chunk:
            time.sleep(0.05)
            continue
        buf += chunk
        if len(buf) < bytes_per:
            continue
        frame = np.frombuffer(buf[:bytes_per], dtype=fmt)
        buf = buf[bytes_per:]

        overall = dbfs(frame)
        bark    = band_dbfs(frame, 500, 2000, AR)
        cry     = band_dbfs(frame, 300, 800, AR)

        if overall >= RMS_DB:
            note(f"LOUD sound: {overall:.1f} dBFS")

        if bark >= BARK_DB:
            note(f"Possible BARK: band 500–2000 Hz {bark:.1f} dB")

        if cry >= CRY_DB:
            note(f"Possible CRY: band 300–800 Hz {cry:.1f} dB")

except KeyboardInterrupt:
    pass
finally:
    proc.kill()
