---
title: "Troubleshooting Arch Linux, Manjaro, and Hardware Failures: A Complete Guide"
date: "2026-08-04T10:00:00+05:30"
categories: ["Linux", "System Administration", "Hardware"]
tags: ["Manjaro", "Arch Linux", "Pacman", "NTFS", "Troubleshooting", "XFCE", "Chkdsk"]
---

Navigating Linux distributions based on Arch—such as Manjaro or CachyOS—offers extreme flexibility and access to cutting-edge software. However, dealing with sudden hardware failures, misconfigurations, and file system corruption can quickly turn a smooth experience into a head-scratcher.

Here is a comprehensive breakdown of everything covered in our recent technical sessions, from mastering package management to fixing corrupted NTFS drives on older hardware.

---

## 1. Pacman Essentials on Arch Linux

`pacman` is the core package manager for Arch Linux and its derivatives. Memorizing these essential commands helps keep your system updated and clean.

* **System Updates:**
Sync repository databases and upgrade all installed packages:
`sudo pacman -Syu`
* **Installing & Removing Packages:**
* Install a specific package: `sudo pacman -S package_name`
* Remove a package: `sudo pacman -R package_name`
* Remove a package and its unused dependencies: `sudo pacman -Rs package_name`
* Remove a package, its configuration files, and unused dependencies: `sudo pacman -Rns package_name`


* **Searching & Maintenance:**
* Search remote repositories: `pacman -Ss keyword`
* Search locally installed packages: `pacman -Qs keyword`
* Clean cached package files to free disk space: `sudo pacman -Sc`



---

## 2. Resolving CachyOS Offline & Online Installation Issues

CachyOS relies heavily on an active internet connection to pull optimized, up-to-date packages during installation.

### Working Around Internet Dropping

* **Toggle Interfaces:** Re-enable Wi-Fi using the tray icon or plug in an Ethernet cable.
* **USB Tethering:** Connect your smartphone via USB, open your phone's settings, and enable **USB Tethering**. Linux detects this as a standard wired connection automatically.
* **Terminal Utility:** Use the built-in text interface:
`sudo nmtui`
* **Offline Mode:** If no connection is possible, select **CachyOS (Offline)** from the boot menu to install the base desktop environment from the USB drive.

---

## 3. Manjaro Administration: Pamac, Printers, and XFCE Tweaks

Manjaro builds on Arch but adds dedicated tools like `pamac` and `mhwd`.

### Package & Hardware Management

* **Update System:** `pamac upgrade`
* **Install/Remove:** `pamac install package_name` / `pamac remove package_name`
* **AUR Updates:** `pamac upgrade -a`
* **Kernel Management:** Check installed kernels with `mhwd-kernel -li` or install a new one via `sudo mhwd-kernel -i linux61`.

### HP LaserJet P1108 Printer Setup

HP printers like the P1108 require a proprietary plugin along with the HPLIP suite:

1. Install dependencies: `pamac install hplip base-devel`
2. Configure printer and download firmware: `sudo hp-setup -i`
3. Enable print queue service: `sudo systemctl enable --now cups.service`
4. Add user to printing group: `sudo gpasswd -a $USER lp`

### XFCE Desktop Performance & NetSpeed Tweaks

* **Fix Tearing/Lag:** Go to **Settings > Window Manager Tweaks > Compositor** and uncheck **Enable display compositing**.
* **Modern Taskbar:** Install `xfce4-docklike-plugin` or switch to the **Whisker Menu**.
* **Network Speed Panel Monitor:**
1. Install the plugin: `pamac install xfce4-netload-plugin`
2. Right-click panel > **Panel > Add New Items > Network Monitor**.
3. In properties, set your active interface name (found via `ip link`, e.g., `enp3s0` or `wlan0`).



---

## 4. Hardware Failures: Dead CMOS Battery, System Clock, and Power Cuts

Older PCs face unique issues when power cuts strike, especially if the motherboards have dead CMOS batteries (CR2032).

### The Root Cause

A dead CMOS battery resets the BIOS hardware clock (RTC) on power loss. When Linux boots with a date set to 1970 or 2000, **SSL connections fail**, package managers crash, and file systems lock up due to invalid timestamps.

### Fixing System Time & Syncing

1. Set the timezone (e.g., IST):
`sudo timedatectl set-timezone Asia/Kolkata`
2. Force manual date setting:
`sudo timedatectl set-time "2026-08-04 18:15:00"`
3. Enable Network Time Protocol (NTP):
`sudo systemctl restart systemd-timesyncd`
`sudo timedatectl set-ntp true`
4. Write correct time to BIOS hardware clock:
`sudo hwclock --systohc`

For custom NTP servers (like NIC networks in India):
Edit `/etc/systemd/timesyncd.conf` and set `NTP=samay1.nic.in samay2.nic.in in.pool.ntp.org`.

---

## 5. Repairing Corrupted NTFS Partitions in Linux

When power cuts occur while Windows or Linux is accessing an NTFS drive, the partition gets marked as "dirty" or corrupts its superblock, throwing errors like `Failed to mount "285 GB Volume"`.

### Step-by-Step NTFS Recovery

1. **Clear Dirty Bit via Linux:**
Install `ntfs-3g` and run `ntfsfix`:
`sudo pacman -S ntfs-3g`
`sudo ntfsfix -d /dev/sda4`
2. **Force Mount (Read-Only Recovery):**
If file systems remain locked, bypass hibernation checks to save your data:
`sudo mkdir -p /mnt/recovery`
`sudo mount -t ntfs-3g -o ro,remove_hiberfile /dev/sda4 /mnt/recovery`
3. **Check Hard Drive Health:**
If `ntfsfix` fails, check if the physical disk has bad sectors using `smartmontools`:
`sudo pacman -S smartmontools`
`sudo smartctl -H /dev/sda`
`sudo smartctl -A /dev/sda`
*(Pay close attention to **Reallocated_Sector_Ct** and **Current_Pending_Sector** values).*

---

## 6. Running `chkdsk` Using a Windows 11 ISO and Ventoy

When Linux tools cannot rebuild damaged NTFS metadata, Windows' native `chkdsk` utility is required.

### Repair Process

1. Boot into your **Ventoy USB** formatted in **MBR mode** (for older BIOS compatibility).
2. Select the **Windows 11 ISO**.
3. On the setup screen, press **Shift + F10** to open the Command Prompt.
4. Identify your partition drive letter:
```cmd
diskpart
list volume
exit

```


5. Run the repair command (replace `X:` with your drive letter):
`chkdsk X: /f /r`
6. Reboot back into Linux, reset your system clock, and mount your repaired partition.

---

### Final Recommendation

For older desktop hardware prone to power cuts:

* Replace the **CR2032 CMOS battery**.
* Use a **UPS** to prevent sudden power loss.
* Format non-Windows storage drives to **Ext4**, which utilizes modern journaling to survive sudden power outages far better than legacy NTFS partitions.
