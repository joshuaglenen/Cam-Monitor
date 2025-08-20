# Baby Monitor

This project includes the design for a wireless camera with soc which connects to a handheld mointor with an optional phone pairing. Below are three sections:
<li> A tutorial to connect an existing rtsp enabled camera to a custom monitor with motion/sound detection </li>
<li> The design of a 4 axis rotating hd camera paired to a portable tablet monitor </li>
<li> Design documents illustrating the block diagram, circuit, pcb layout, and bill of materials </li>

# Monitor Prototype using Commmercial RTSP Camera
This setup turns an Orange Pi Zero 3 into a dedicated baby monitor viewer with optional motion and audio detection, using a commercial RTSP-capable IP camera.

The Orange Pi runs Debian Xfce, displays the camera feed full-screen on an external HDMI monitor, and can optionally run OpenCV-based detection in the background (just sends a terminal message for now but can be altered to send a phone notification/text with an external app or paid service).

### Tested configuration:
  <li>Video latency: ~500 ms </li>
  <li>Stream: 1080p @ 30 FPS (RTSP over TCP) </li>
  <li>Stable Wi-Fi after disabling power save </li>
  <li>Passive heatsink added to reduce CPU temperature </li>

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


### Loud noise detection using audio_detector.py
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
  ExecStart=/usr/bin/python3 /home/orangepi/audio_detector.py
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
  Environment=RTSP_URL=rtsp://user:pass@IP:PORT/stream2
  Environment=MIN_AREA=0.001
  WorkingDirectory=/home/orangepi
  ExecStart=/usr/bin/python3 /home/orangepi/motion_detector.py
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

This project was developed to create a compact embedded system capable of image capture, wireless communication, and real-time monitoring for the purpose of a baby/pet/security monitor. The process began with a requirement analysis, power budget, performance constraints, and component selection. A high-level block diagram (Figure 1) was used to outline the relationships between the chosen system-on-chip (SoC), memory, camera interface, power regulation, and communication subsystems.

Next, a full schematic design (Figure 2) was completed. Critical modules included:

    A BGA SoC with external DDR3 memory and eMMC storage.
    
    A camera sensor connected via MIPI CSI through an FFC connector.
    
    A Wi-Fi/Bluetooth module for connectivity.
    
    A power management stage using a USB-C input, fuse, and switching regulators.
    
    Supporting peripherals including an audio codec, microphone, infrared LED driver, and servo interfaces.

Each functional block was designed with placement and routing considerations in mind. For high-speed components such as DDR3, eMMC, and MIPI CSI, trace length matching and impedance-controlled routing rules were implemented for signal integrity. The Wi-Fi module was positioned at the PCB edge to allow for an external antenna connection. JST connectors were chosen for plug in connections to motors/speaker/IR LEDs and placed on the board exterior. Components were placed in modules grouping on an eight layer pcb with separate ground and power planes. Care was taken to separate the noisy systems from the sensitive data lines. Throughout development, iterative design checks and design rule verifications were carried out to conform to manufacturing standards and reliability.

# Design Documents

The system design is supported by the following:

    Figure 1: High-level block diagram of the system architecture.

    Figure 2: Circuit schematic of the camera board.

    Figure 3: Camera board PCB layout.

These figures and the accompanying table provide a clear overview of both the hardware structure and the detailed implementation.

<img width="656" height="891" alt="Untitled Diagram drawio" src="https://github.com/user-attachments/assets/1ea75fdb-b6c4-4d59-96cb-ded9808747e3" />


Fig 1: System Block Diagram

<img width="4414" height="3118" alt="Untitled" src="https://github.com/user-attachments/assets/bf781b42-f123-4652-b1ce-7aaa05d2626a" />


Fig 2: Circuit Diagram for the Camera Board

<img width="1309" height="843" alt="Capture" src="https://github.com/user-attachments/assets/5e74a335-2cde-4065-a710-395b9c99fbbc" />


Fig 3: PCB Diagram for the Camera Board
