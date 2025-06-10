# Mediatek Porting Tool 

### This Tool is maintained by the T-ROM Project

#### Required programs :

-Python 3.12.x (for Windows users, install Python from the Microsoft Store)

#### How to use it:

1.Download the repository

2.Start Run.bat (on Windows) or Run.sh (on Linux)

3. Select Chiptype to : "Kernel only (only replace kernel)" when porting for Timmkoo Q5 / Q3e devices (2020-2024)

### Warning !!!
Make sure your porting rom zip you want to port has the kernel version 3.10.54 otherwise it can go wrong.
### Warning !!!

5. Click on "One-Click Port"

6. Give your Paths for your port Rom .zip

7. Give your Paths to your devices system.img and boot.img

8. When its finished porting , you found the generated images in /out of the tools directory

### Warning !!!
You need to boot once complete in the android 5 system before flashing the generated Images (Important for later)
### Warning !!!

10. Flash the generated images to your device over the android 5 system with **[SP Flashtool](https://spflashtools.com/windows/sp-flash-tool-v5-1924)** (Download Only )

#### On your Timmkoo after flashing the generated images :
 
10. Boot straight into Twrp (Vol+ and Power button)

11. Go to wipe - advanced wipe - then select cache and click on wipe

12. Then Go to wipe - Format data - write yes and click on format data

13. Then go to wipe - swipe to  normal wipe /factory reset - reboot system

14. If it goes according to plan it should boot normal (takes time )

15. When it goes wrong (display,etc.), try it with a different zip rom

#### This Tool was translated from Chinese into English 

#### The Tool Developers :
- **[Steve ZMT Studio](https://github.com/SteveZMTstudios)**
- **[affggh](https://github.com/affggh)**
- **[ColdWindScholar](https://github.com/ColdWindScholar)**
#### Translations :
- **[Palutenfan123](https://github.com/timmkoo)**
