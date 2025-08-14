# Baby Monitor

This project includes the design for a wireless camera with soc which connects to a handheld mointor with an optional phone pairing. Below are three sections:
<cl> A tutorial to connect an existing rtsp enabled camera to a custom monitor with motion/sound detection </cl>
<cl> The design of a 2 axis rotating hd camera paired to a portable tablet monitor </cl>
<cl> Design documents illustrating the circuit, pcb layout, and bill of materials </cl>

# Monitor prototype using commmercial rtsp camera
This setup turns an Orange Pi Zero 3 into a dedicated baby monitor viewer with optional motion and audio detection, using a commercial RTSP-capable IP camera.

The Orange Pi runs Debian Xfce, displays the camera feed full-screen on an external HDMI monitor, and can optionally run OpenCV-based detection in the background.
Power for both the SBC and monitor comes from a USB wall charger.

### Tested configuration:
  <cl>Video latency: ~500 ms </cl>
  <cl>Stream: 1080p @ 30 FPS (RTSP over TCP) </cl>
  <cl>Stable Wi-Fi after disabling power save </cl>
 <cl> Passive heatsink added to reduce CPU temperature </cl>

### Install base os and packages
[Debian XCFE](https://sd-card-images.johang.se/boards/orange_pi_zero3.html)
sudo apt update && sudo apt upgrade -y
sudo apt install sudo curl wget git htop net-tools ffmpeg mpv python3-opencv python3-numpy

### Stop power save mode from cutting wifi feed

  sudo nano /etc/systemd/system/wifi-powersave-off.service
  
      [Unit]
      Description=Disable WiFi power save
      After=network.target
      
      [Service]
      Type=oneshot
      ExecStart=/sbin/iw dev wlan0 set power_save off
      RemainAfterExit=yes
      
      [Install]
      WantedBy=multi-user.target
    
  sudo systemctl enable wifi-powersave-off.service
  sudo systemctl start wifi-powersave-off.service

### Create rtsp script

  mkdir -p ~/bin
  nano ~/bin/start-rtsp.sh
  
      #use username and password for your camera along with its ip and port 
      URL="rtsp://user:pass@IP:PORT/stream1"
      
      # add your ip
      for i in {1..60}; do
        ping -c1 -W1 IP >/dev/null && break
        sleep 1
      done
      
      # Needed when launching from systemd into your X session
      export DISPLAY=:0
      
      # Run ffplay full‑screen; low‑latency, TCP for stability
      exec ffplay -fs -nostats \
        -fflags nobuffer -flags low_delay -fast \
        -rtsp_transport tcp "$URL"
        
  chmod +x ~/bin/start-rtsp.sh

### Autostart at boot
  chmod +x ~/bin/start-rtsp.sh
  sudo nano /etc/systemd/system/rtsp-view.service
  
      [Unit]
      Description=Start RTSP viewer (ffplay) full-screen
      After=graphical.target network-online.target
      Wants=network-online.target
      
      [Service]
      Type=simple
      User=orangepi
      Environment=DISPLAY=:0
      ExecStart=/home/orangepi/bin/start-rtsp.sh
      Restart=always
      RestartSec=3
      
      [Install]
      WantedBy=graphical.target
      
  sudo systemctl enable rtsp-view
  sudo systemctl start rtsp-view


### Loud noise detection using audio_detect.py
  cat <<'SERVICE' | sudo tee /etc/systemd/system/audio-detector.service
  [Unit]
  Description=RTSP Audio Detector (bark/cry bands)
  After=network-online.target
  
  [Service]
  Environment=RTSP_URL=rtsp://user:pass@IP:PORT/stream2
  Environment=RMS_DB=-25
  Environment=BARK_DB=-30
  Environment=CRY_DB=-32
  Environment=COOLDOWN=5
  ExecStart=/usr/bin/python3 /home/orangepi/audio_detect.py
  Restart=always
  RestartSec=2
  User=orangepi
  Group=orangepi
  
  [Install]
  WantedBy=multi-user.target
  SERVICE
  
  sudo systemctl daemon-reload
  sudo systemctl enable --now audio-detector
  journalctl -u audio-detector -f

### Motion dectection using motion-detector.py
  cat <<'SERVICE' | sudo tee /etc/systemd/system/motion-detector.service
  [Unit]
  Description=Simple Motion Detector (OpenCV, no models)
  After=network-online.target
  
  [Service]
  Environment=RTSP_URL=rtsp://joshglenen:joshglenen@192.168.2.247:554/stream2
  Environment=MIN_AREA=0.001
  WorkingDirectory=/home/orangepi
  ExecStart=/usr/bin/python3 /home/orangepi/motion_detect.py
  Restart=always
  RestartSec=2
  User=orangepi
  Group=orangepi
  
  [Install]
  WantedBy=multi-user.target
  SERVICE
  
  sudo systemctl daemon-reload
  sudo systemctl enable --now motion-detector
  journalctl -u motion-detector -f

# Design Methods

# Design Documents
