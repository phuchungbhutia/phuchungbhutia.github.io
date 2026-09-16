---

title: "HP Printer Problems on Linux Mint: HPLIP, Device Not Detected, Drivers from Tarballs, CUPS, and hp-setup"
date: "2026-09-16"
categories: ["Linux", "Hardware"]
tags: ["linux-mint", "hp-printer", "hplip", "cups", "hp-setup", "driver", "tarball", "troubleshooting", "howto", "2026"]
description: "A practical troubleshooting guide to resolving HP printer detection failures, installing proprietary plugins, compiling tarball drivers, and configuring CUPS on Linux Mint."

---

# HP Printer Problems on Linux Mint: HPLIP, Device Not Detected, Drivers from Tarballs, CUPS, and hp-setup

HP printers on Linux Mint generally offer broad driver support via the open-source HP Linux Imaging and Printing (HPLIP) suite. However, users frequently encounter edge cases: HPLIP failing to discover a connected USB or network device, print jobs stalling with generic "Filter failed" errors in the Common UNIX Printing System (CUPS), missing proprietary binary plugins, or newer hardware models requiring source-compiled tarballs.

This guide details the complete diagnostic and resolution workflow for HP printing on Linux Mint. It covers hardware-level bus verification, official package repository setup, interactive execution of `hp-setup`, manual compilation of upstream tarballs, and fallback queue configuration using the native CUPS administration interface.

---

## 1. The Linux Printing Stack for HP Devices

Understanding how printing requests travel through the operating system isolates the point of failure:

* **HPLIP (HP Linux Imaging and Printing):** An HP-developed suite providing low-level communication backends (`hp:/usb/...`, `hp:/net/...`), device status monitors, scanning drivers via SANE, and setup utilities (`hp-setup`, `hp-plugin`).
* **CUPS (Common UNIX Printing System):** The underlying print scheduler that manages queues, accepts print jobs from desktop applications, converts document formats, and dispatches rasterized streams to backends.
* **PPD (PostScript Printer Description) Files:** Device configuration files defining hardware-supported resolutions, paper trays, media types, color spaces, and duplex units.
* **Proprietary Binary Plugin:** Closed-source firmware files required by specific HP LaserJet and multi-function printer (MFP) models for software rasterization. Without this plugin, CUPS queues fail immediately.

---

## 2. Install the Base Printing Stack and HPLIP

Linux Mint provides tested builds of HPLIP and CUPS in its official software repositories.

Open a terminal and install the core printing subsystem:

```bash
sudo apt update

# Core CUPS infrastructure and system management GUI
sudo apt install -y cups cups-client cups-bsd system-config-printer

# HPLIP software suite and GUI utilities
sudo apt install -y hplip hplip-gui printer-driver-all

# Network mDNS discovery and modern IPP-over-USB daemons
sudo apt install -y avahi-daemon ipp-usb

```

Enable and start the primary system services:

```bash
sudo systemctl enable --now cups
sudo systemctl enable --now avahi-daemon

```

Verify service status:

```bash
systemctl status cups --no-pager
systemctl status avahi-daemon --no-pager

```

---

## 3. Configure Administrative Permissions (`lpadmin`)

Managing CUPS queues, altering driver assignments, and configuring printers through graphical tools require membership in the `lpadmin` group.

Add your active user account to `lpadmin`:

```bash
sudo usermod -aG lpadmin "$USER"

```

> **Important:** Group modifications take effect on the next login. Log out and log back in, or restart the workstation, before continuing.

Verify that your user account has the required group membership:

```bash
groups "$USER"

```

Confirm that `lpadmin` appears in the returned list.

---

## 4. Hardware-Level Device Verification

Before debugging print software, verify that the Linux kernel detects the physical printer hardware.

### 4.1 USB Connected Printers

Inspect the system USB bus:

```bash
lsusb

```

Look for an entry containing `Hewlett-Packard` or `HP`. Then, query the backends recognized by CUPS:

```bash
lpinfo -v

```

A recognized printer will return a URI such as:

```text
direct usb://HP/LaserJet%20Professional%20P1102w?serial=000000000
direct hp:/usb/HP_LaserJet_Professional_P1102w?serial=000000000

```

If the device is not listed:

1. Re-seat the USB cable or connect to an alternate USB port on the motherboard (avoid unpowered external hubs).
2. Check whether `ipp-usb` has claimed the device exclusively:
```bash
systemctl status ipp-usb

```


3. Restart CUPS:
```bash
sudo systemctl restart cups

```


4. Re-run `lpinfo -v`.

### 4.2 Network Connected Printers (Ethernet or Wi-Fi)

Obtain the printer's assigned IP address from the front panel display or your local router's DHCP client table. Verify basic ICMP network reachability:

```bash
ping -c 3 <printer-ip>

```

Use HPLIP's network discovery tool to scan the local subnet:

```bash
hp-probe -bnet

```

This utility lists discovered HP devices along with their network URIs and hardware models.

---

## 5. Configure the Printer via `hp-setup`

The primary method for configuring an HP printer is `hp-setup`, an interactive utility that handles URI discovery, PPD assignment, and automated plugin retrieval.

Run the tool in interactive terminal mode:

```bash
sudo hp-setup -i

```

1. **Select Connection Type:** Choose option `0` for USB, or option `1` for Network/Ethernet/Wireless.
2. **Device Discovery:** For network setups, enter the printer's static IP address if the broadcast scan does not locate it.
3. **Proprietary Plugin Prompt:** If prompted that your printer model requires a proprietary binary plugin, choose to download the plugin from the official HP server and accept the licensing terms.
4. **Queue Parameters:** Provide a clear printer name, description, and physical location.
5. **Finalize Setup:** Print a test page when prompted to verify that the queue functions correctly.

---

## 6. Resolving HPLIP Detection Failures

If `hp-setup` reports `No installed HP devices found` despite physical hardware presence:

### 6.1 Clean Reinstallation of HPLIP

Corrupted configuration caches or partial dependencies can prevent device enumeration:

```bash
# Purge existing packages
sudo apt remove --purge -y hplip hplip-gui

# Clean orphaned packages
sudo apt autoremove -y

# Reinstall base packages
sudo apt update
sudo apt install -y hplip hplip-gui printer-driver-all

# Restart services
sudo systemctl restart cups
sudo systemctl restart avahi-daemon

```

### 6.2 Manual Plugin Installation

If the interactive installer hangs while retrieving binary plugins, invoke the dedicated plugin installer directly:

```bash
sudo hp-plugin -i

```

Choose to download the plugin automatically from HP, accept the EULA, and verify that the installation completes without network timeout errors. Once finished, re-run:

```bash
sudo hp-setup -i

```

---

## 7. Installing HP Drivers from Tarballs

When managing newer HP printer models not supported by the default Linux Mint package repository, install upstream drivers manually.

### Case A: Compiling Upstream HPLIP from Source (`hplip-*.tar.gz`)

Download the latest release tarball from the [HPLIP source portal](https://developers.hp.com/hp-linux-imaging-and-printing/get-started).

Install all necessary build dependencies and development headers:

```bash
sudo apt update
sudo apt install -y \
  libcups2-dev cups cups-bsd cups-client \
  avahi-utils libavahi-client-dev \
  libdbus-1-dev build-essential \
  ghostscript openssl libssl-dev libjpeg-dev \
  libsnmp-dev snmp-mibs-downloader \
  libtool libusb-1.0-0-dev \
  wget python3 python3-dbus python3-pyqt5 \
  python3-reportlab python3-notify2 \
  python3-lxml python3-dev python3-pil \
  libsane-dev sane-utils

```

Extract the source archive, compile the suite, and install the binaries:

```bash
cd ~/Downloads
tar -xzvf hplip-*.tar.gz
cd hplip-*/

# Configure build flags for modern Mint/Debian installations
./configure --prefix=/usr --disable-qt4 --enable-qt5

# Compile using all available CPU threads
make -j"$(nproc)"

# Install system files
sudo make install

```

Restart the system print spooler and run the setup wizard:

```bash
sudo systemctl restart cups
sudo hp-setup -i

```

### Case B: Model-Specific Driver Archives (e.g., HP Laser MFP 130 Series)

Certain modern monochrome lasers and multifunction devices (including legacy Samsung-derived models) are distributed as standalone vendor archives containing shell scripts or raw `.deb` files:

1. Download the model-specific tarball from HP Customer Support.
2. Extract the archive contents:
```bash
cd ~/Downloads
tar -xzvf hp-driver-*.tar.gz
cd hp-driver-*/
ls -la

```


3. **If `.deb` packages are present:**
```bash
sudo apt install ./*.deb
sudo systemctl restart cups

```


4. **If an `install.sh` script is provided:**
```bash
chmod +x install.sh
sudo ./install.sh
sudo systemctl restart cups

```


5. Follow the terminal prompts, agree to the software license, and complete the device registration.

---

## 8. Fallback Configuration via CUPS Web Administration

If `hp-setup` cannot register the printer, configure the queue manually through the local CUPS administrative console.

1. Open a browser and navigate to:
```text
http://localhost:631

```


2. Navigate to **Administration → Add Printer**.
3. Authenticate using your Linux system username and password (requires membership in `lpadmin`).
4. Select the connection protocol:
* **Local USB:** Select the auto-detected HP USB entry.
* **Network Device:** Select **AppSocket/HP JetDirect** (URI: `socket://<printer-ip>:9100`) or **Internet Printing Protocol (ipp)** (URI: `ipp://<printer-ip>/ipp/print`).


5. Click **Continue**.
6. Provide a system name, descriptive label, and physical location.
7. Assign the driver:
* Choose **HP** under the manufacturer list and locate your exact model.
* Alternatively, choose **Provide a PPD File** and point to the `.ppd` file located inside your extracted driver directory or `/usr/share/ppd/HP/`.


8. Click **Add Printer**, set default media and paper tray options, and submit a test page.

---

## 9. Common Errors and Solutions

### 9.1 Print Jobs Terminate with "Filter Failed"

This error indicates that the rasterization filter crashed or was blocked by a missing dependency or plugin.

1. Inspect the last 50 lines of the CUPS error log:
```bash
sudo tail -n 50 /var/log/cups/error_log

```


2. Cancel stalled jobs:
```bash
sudo cancel -a YourPrinterName

```


3. For HP LaserJet models that require software rasterization, ensure the binary plugin is up to date:
```bash
sudo hp-plugin -i

```


4. If using standard network protocols, re-add the printer in the CUPS web interface using the generic **IPP Everywhere** driver.

### 9.2 Printer Functions on Windows but Fails on Linux

If network printing works on Windows but Linux clients cannot communicate with the device:

1. Verify network reachability with `ping <printer-ip>`.
2. Access the printer's Embedded Web Server (EWS) by typing its IP address into a web browser.
3. Verify that **IPP Printing** and **Raw Port 9100 (AppSocket/JetDirect)** are enabled under the network settings.
4. Disable any proprietary "HP Smart" or secure authentication modes that restrict printing to vendor desktop applications.

---

## 10. Automated Environment Setup Script

Save the following bash script as `setup-hp-printer-mint.sh` to install all necessary packages, enable required services, and grant user permissions in a single run:

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== Updating package index ==="
sudo apt update

echo "=== Installing CUPS and HPLIP packages ==="
sudo apt install -y cups cups-client cups-bsd \
                    system-config-printer \
                    avahi-daemon ipp-usb \
                    hplip hplip-gui \
                    printer-driver-all

echo "=== Enabling printing and discovery services ==="
sudo systemctl enable --now cups
sudo systemctl enable --now avahi-daemon

echo "=== Adding current user to lpadmin group ==="
sudo usermod -aG lpadmin "$USER"

echo "=== Setup complete ==="
echo "Log out and log back in to apply group changes."
echo "Then connect your printer and run: sudo hp-setup -i"

```

Make the script executable and run it:

```bash
chmod +x setup-hp-printer-mint.sh
./setup-hp-printer-mint.sh

```

---

## 11. Command Reference

| Task | Command |
| --- | --- |
| Verify USB hardware bus | `lsusb` |
| Probe network HP devices | `hp-probe -bnet` |
| View CUPS-recognized backends | `lpinfo -v` |
| Run interactive HPLIP setup | `sudo hp-setup -i` |
| Install proprietary binary plugin | `sudo hp-plugin -i` |
| Execute HPLIP diagnostics | `hp-check -r` |
| Display printer queue status | `lpstat -p -d` |
| List active print jobs | `lpq` |
| Cancel all active print jobs | `sudo cancel -a` |
| Inspect CUPS error logs | `sudo tail -f /var/log/cups/error_log` |
| Restart the CUPS service | `sudo systemctl restart cups` |

---

## References

1. [HP Linux Imaging and Printing (HPLIP) Portal](https://developers.hp.com/hp-linux-imaging-and-printing)
2. [HPLIP Binary Plugin Documentation](https://developers.hp.com/hp-linux-imaging-and-printing/binary-plugin.html)
3. [OpenPrinting CUPS Documentation](https://openprinting.github.io/cups/)
4. [Linux Mint Printing and Driver Documentation](https://linuxmint-user-guide.readthedocs.io/en/latest/)
5. [Ubuntu Community Help: Troubleshooting HPLIP and CUPS](https://www.google.com/search?q=https://help.ubuntu.com/community/HpLIP)
