#!/usr/bin/env python3
import os, time, cv2, datetime, numpy as np

# ---------- CONFIG (override via env vars) ----------
RTSP_URL = os.environ.get("RTSP_URL", "rtsp://joshglenen:joshglenen@192.168.2.247:554/stream2")
TARGET_W = int(os.environ.get("TARGET_W", "640"))   # resize width for speed
THRESH   = int(os.environ.get("THRESH", "35"))      # binarize threshold (0-255)
MIN_AREA = float(os.environ.get("MIN_AREA", "0.002"))  # motion area as fraction of frame (e.g., 0.002 = 0.2%)
COOLDOWN = float(os.environ.get("COOLDOWN", "3"))   # seconds between prints
SHOW     = os.environ.get("SHOW", "0") == "1"       # set SHOW=1 to see debug window
ERODE    = int(os.environ.get("ERODE", "1"))        # morphology passes
DILATE   = int(os.environ.get("DILATE", "3"))
LEARN    = float(os.environ.get("LEARN", "-1"))     # MOG2 learningRate; -1=auto, 0=frozen bg
MASK_POLY = os.environ.get("MASK_POLY", "")         # e.g. "50,200;500,200;500,360;50,360"

# ---------- helpers ----------
def parse_poly(s):
    if not s: return None
    pts = []
    for p in s.split(";"):
        x,y = p.split(",")
        pts.append([int(x), int(y)])
    return np.array([pts], dtype=np.int32)

def notify(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)

# ---------- open stream with auto-reconnect ----------
def open_cap():
    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    return cap if cap.isOpened() else None

cap = open_cap()
if cap is None:
    raise SystemExit(f"Cannot open stream: {RTSP_URL}")

mog = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=16, detectShadows=True)

last_print = 0.0
region = None

while True:
    ok, frame = cap.read()
    if not ok:
        # brief backoff + reconnect
        time.sleep(0.2)
        cap.release()
        cap = open_cap()
        continue

    # resize
    h, w = frame.shape[:2]
    if w != TARGET_W:
        r = TARGET_W / float(w)
        frame = cv2.resize(frame, (TARGET_W, int(h*r)))
        h, w = frame.shape[:2]

    # build mask polygon (if provided, only run motion inside it)
    if MASK_POLY and region is None:
        region = parse_poly(MASK_POLY)
        if region is not None:
            # scale polygon if it was given for original size; here we assume coords are for resized frame
            pass

    # foreground mask
    fg = mog.apply(frame, learningRate=LEARN)

    # shadows are 127 -> binarize more aggressively
    _, binm = cv2.threshold(fg, THRESH, 255, cv2.THRESH_BINARY)

    # ROI masking
    if region is not None:
        mask = np.zeros_like(binm)
        cv2.fillPoly(mask, region, 255)
        binm = cv2.bitwise_and(binm, mask)

    # morphology to clean speckle
    if ERODE > 0:
        binm = cv2.erode(binm, None, iterations=ERODE)
    if DILATE > 0:
        binm = cv2.dilate(binm, None, iterations=DILATE)

    # contour area
    contours, _ = cv2.findContours(binm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    area_thresh = int(MIN_AREA * (h*w))
    motion = sum(cv2.contourArea(c) for c in contours if cv2.contourArea(c) >= area_thresh)

    if motion >= area_thresh:
        now = time.time()
        if now - last_print >= COOLDOWN:
            notify(f"MOTION: {int(motion)} px^2 (area ≥ {area_thresh})")
            last_print = now

    if SHOW:
        vis = cv2.addWeighted(frame, 0.8, cv2.cvtColor(binm, cv2.COLOR_GRAY2BGR), 0.5, 0)
        cv2.putText(vis, f"area_th={area_thresh}", (8,16), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1)
        cv2.imshow("motion", vis)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
