# Baby Monitor

This project includes the design for a wireless camera and handheld monitor consisting of the following three sections:
<li> A tutorial to connect an existing rtsp enabled camera to a custom monitor using an H618 SoM with motion/sound detection </li>
<li> The design of an 8 layer RV1126 board which connects to a 1080p 60fps camera and streams the Audio/Video feed over RTSP </li>
<li> The design of an optimized 2.4"x2.4" 6 layer A64 board which recieves the Audio/Video feed and displays it on a Raspberry 5 compatable touchscreen</li>

# Monitor Prototype using Commmercial RTSP Camera
This setup turns an Orange Pi Zero 3 into a dedicated baby monitor viewer with optional motion and audio detection, using a commercial RTSP-capable IP camera.

The Orange Pi runs Debian Xfce, displays the camera feed full-screen on an external HDMI monitor, and can optionally run OpenCV-based detection in the background (just sends a terminal message for now but can be altered to send a phone notification/text with an external app or paid service).

### Tested configuration:
  <li>Video latency: ~500 ms </li>
  <li>Stream: 1080p @ 30 FPS (RTSP over TCP) </li>
  <li>Stable Wi-Fi after disabling power save </li>
  <li>Passive heatsink added to reduce CPU temperature </li>

### Installation Guide:

[Guide](https://github.com/joshuaglenen/Cam-Monitor/blob/main/OrangePi3Zero_Debian_Setup.txt)

# Camera Board

This is a compact embedded system capable of image capture, wireless communication, and real-time monitoring for the purpose of a baby/pet/security monitor. The process began with a requirement analysis, power budget, designation of performance constraints, and component selection. A high-level block diagram (Figure 1) was used to outline the relationships between the chosen SoC, memory, camera interface, power regulation, and communication subsystems.

Next, a full schematic design (Figure 2,3) was completed. Critical modules included:

    A BGA SoC with external DDR3 memory and eMMC storage.
    
    A camera sensor connected via MIPI CSI through an FFC connector.
    
    A Wi-Fi/Bluetooth module for connectivity.
    
    A power management stage using a USB-C input, fuse, and switching regulators.
    
    Supporting peripherals including an audio codec, microphone, infrared LED driver, and servo interfaces.

Each functional block was designed with placement and routing considerations in mind. For high-speed components such as DDR3, eMMC, and MIPI CSI, trace length matching and impedance-controlled routing rules were implemented for signal integrity. The Wi-Fi module was positioned at the PCB edge to allow for an external antenna connection. JST connectors were chosen for plug in connections to motors/speaker/IR LEDs and placed on the board exterior. Components were placed in modules grouping on an eight layer pcb with separate ground and power planes. Care was taken to separate the noisy systems from the sensitive data lines. Throughout development, iterative design checks and design rule verifications were carried out to conform to manufacturing standards and reliability.

<img width="752" height="514" alt="dde" src="https://github.com/user-attachments/assets/ba0f9285-e9bd-4e36-944f-40958a7b080f" />


Fig 1: Camera Board System Block Diagram

<img width="4414" height="3118" alt="Untitled" src="https://github.com/user-attachments/assets/bf781b42-f123-4652-b1ce-7aaa05d2626a" />


Fig 2: Camera Board Circuit Diagram 

<img width="1309" height="843" alt="Capture" src="https://github.com/user-attachments/assets/5e74a335-2cde-4065-a710-395b9c99fbbc" />


Fig 3: Camera Board PCB Diagram

# Monitor Board

This is a 2.4"x2.4" 6 layer tablet SoM board which recieves an RTSP Audio/Video feed and displays it via a touchscreen. It includes an A64 Soc, 8Gb eMMC, 8GB DDR3, 2KB EEPROM, Stereo Speakers, power management chip, WiFi/BLE chip, analog mic/preamp, USB OTG/JTAG, 5000mAh Li-Ion Cell with USB C port.

<img width="761" height="508" alt="sec" src="https://github.com/user-attachments/assets/a8641740-205d-4eb1-8f79-089e4af5a43d" />


Fig 4: Monitor Board System Block Diagram

<img width="4414" height="3118" alt="Untitled" src="https://github.com/user-attachments/assets/91df9114-6c44-4ba1-b3d9-94179a3bdcde" />


Fig 5: Monitor Board Circuit Diagram 

<img width="1037" height="689" alt="Handheld Monitor" src="https://github.com/user-attachments/assets/ec318a5d-bc78-452f-9d11-27cbb4f00aef" />


Fig 6: Monitor Board PCB Diagram Top View

<img width="1047" height="688" alt="Handheld Monitror22" src="https://github.com/user-attachments/assets/312b87a5-1c06-4d0e-8aee-5e336693d86f" />


Fig 7: Monitor Board PCB Diagram Bottom View
