---
title: "Linux Mint XFCE Power-User Setup: Browsers, Editors, Printers, Firewall, Fonts, and Boot Managers"
date: "2026-09-16"
categories: ["Linux", "System Administration"]
tags: ["linux-mint", "xfce", "hplip", "cups", "firewall", "refind", "grub-customizer", "microsoft-fonts", "vscodium", "brave", "opera", "chromium", "2026"]
description: "Step-by-step guide to installing browsers, VSCodium, UFW, HP Laser 1008A drivers, Microsoft fonts, pexec, boot managers, and removing Mozilla packages."

---

# Linux Mint XFCE Power-User Setup: Browsers, Editors, Printers, Firewall, Fonts, and Boot Managers

This guide provides step-by-step procedures for configuring a production-ready Linux Mint XFCE desktop. It covers installing privacy-focused browsers and code editors, securing network traffic with an uncomplicated firewall, resolving proprietary printer driver requirements, adding core typography assets, configuring parallel job automation, managing UEFI bootloaders, and cleanly purging Mozilla packages on restricted networks.

---

## 1. System Refresh and Base Upgrades

Refreshing local package indices and upgrading existing binaries ensures that all base libraries are current, reducing potential dependency conflicts during subsequent installations.

Execute the following commands in your terminal:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y

```

---

## 2. Browser Deployments: Opera, Brave, and Chromium

Deploying specialized Chromium-based browsers offers varying balances of privacy, utility, and standard web compatibility.

### 2.1 Opera

Opera features a built-in ad blocker, an integrated VPN proxy, and productivity sidebars. Add its official repository and signing key:

```bash
# Import GPG key
wget -qO- https://deb.opera.com/archive.key | \
  gpg --dearmor | \
  sudo dd of=/usr/share/keyrings/opera-browser.gpg

# Add official repository
echo "deb [signed-by=/usr/share/keyrings/opera-browser.gpg] https://deb.opera.com/opera-stable/ stable non-free" | \
  sudo dd of=/etc/apt/sources.list.d/opera-archive.list

# Update indices and install
sudo apt update
sudo apt install -y opera-stable

```

Launch the browser via the desktop application menu or by running `opera`.

### 2.2 Brave Browser

Brave enforces aggressive tracker blocking and privacy defaults out of the box. Install it via the vendor's APT repository:

```bash
sudo apt install -y curl

# Import official keyring
sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg \
  https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg

# Add repository source list
sudo curl -fsSLo /etc/apt/sources.list.d/brave-browser-release.sources \
  https://brave-browser-apt-release.s3.brave.com/brave-browser.sources

# Update indices and install
sudo apt update
sudo apt install -y brave-browser

```

Launch the browser using `brave-browser` or select it from the system menu.

### 2.3 Chromium

Chromium provides an open-source, unbranded base ideal for extension verification and general browsing.

Install native distribution binaries directly from the system repositories:

```bash
sudo apt update
sudo apt install -y chromium

```

If package names differ on your specific distribution release, use:

```bash
sudo apt install -y chromium-browser

```

If you prefer isolated containerization via Snap:

```bash
sudo apt install -y snapd
sudo snap install chromium

```

---

## 3. Install VSCodium (Telemetry-Free Code Editor)

VSCodium provides community-driven, telemetry-disabled binaries built directly from Microsoft's open-source `vscode` repository.

### 3.1 APT Repository Method

```bash
# Install core transport dependencies
sudo apt update
sudo apt install -y curl gnupg apt-transport-https

# Import GPG verification key
curl -fsSL https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/raw/master/pub.gpg | \
  gpg --dearmor | \
  sudo tee /usr/share/keyrings/vscodium.gpg > /dev/null

# Register the software repository
echo "deb [signed-by=/usr/share/keyrings/vscodium.gpg] https://download.vscodium.com/debs vscodium main" | \
  sudo tee /etc/apt/sources.list.d/vscodium.list

# Update indices and install
sudo apt update
sudo apt install -y codium

```

Launch the editor using `codium`.

### 3.2 Flatpak Method (Alternative)

For containerized application isolation, deploy via Flathub:

```bash
sudo apt install -y flatpak
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install -y flathub com.vscodium.codium

```

Run the containerized application:

```bash
flatpak run com.vscodium.codium

```

---

## 4. Enable and Configure the UFW Firewall

The Uncomplicated Firewall (UFW) manages iptables and nftables packet filtering rules to protect your system from unsolicited incoming network traffic.

### 4.1 CLI Configuration

Check current status:

```bash
sudo ufw status verbose

```

Enforce a default drop policy on all incoming traffic while allowing outgoing communication:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing

```

> **Important:** If managing this system remotely, explicitly open port 22 or your custom SSH port prior to activating the firewall to avoid immediate lockouts.

```bash
# Allow SSH access
sudo ufw allow ssh

# Allow web services (if hosting local servers)
sudo ufw allow http
sudo ufw allow https

# Enable the firewall service
sudo ufw enable

```

Confirm running status and active firewall rules:

```bash
sudo ufw status numbered

```

### 4.2 Optional Graphical Interface

For a visual firewall management interface:

```bash
sudo apt install -y gufw

```

Open **Firewall Configuration** from the system settings menu to manage rules visually.

---

## 5. HP Laser 1008A Setup: HPLIP, CUPS, and Driver Plugins

Monochrome laser printers such as the HP Laser 1008A utilize the Common UNIX Printing System (CUPS) combined with HP Linux Imaging and Printing (HPLIP) software stacks, often requiring a proprietary firmware binary plugin.

### 5.1 Service and Tool Installation

Install the CUPS spooler subsystem and HPLIP utilities:

```bash
sudo apt update
sudo apt install -y cups cups-client cups-bsd hplip hplip-gui

```

Enable and start the CUPS system daemon:

```bash
sudo systemctl enable --now cups

```

Verify service status:

```bash
systemctl status cups

```

### 5.2 Device Registration

Connect the printer via USB (or verify network connectivity), then invoke the setup wizard:

```bash
hp-setup

```

Select your connection transport (`USB` or `Network/Ethernet/Wireless`) and follow the on-screen configuration prompts.

To locate network-attached HP hardware across local subnets:

```bash
hp-probe -bnet

```

### 5.3 Proprietary Plugin Installation

Certain HP LaserJet models require non-free firmware blobs to complete rasterization. If prompted by `hp-setup` or diagnostic checks, install the plugin manually:

```bash
sudo hp-plugin -i

```

Complete the terminal prompts to fetch and verify the plugin, then rerun `hp-setup`.

### 5.4 Administrative Configuration via CUPS Web Interface

Printers can also be managed directly through the local CUPS administrative console:

1. Open your browser and navigate to `http://localhost:631`.
2. Navigate to **Administration → Add Printer**.
3. Authenticate using your local administrator credentials.
4. Select the detected HP Laser 1008A device.
5. Assign the corresponding HPLIP PPD driver profile and print a test page.

### 5.5 Diagnostics and Status Checking

Display queue status:

```bash
lpstat -p -d

```

Restart the print daemon if jobs hang:

```bash
sudo systemctl restart cups

```

Execute an automated system-wide printing check:

```bash
hp-check -t

```

---

## 6. Install Microsoft TrueType Core Fonts

Installing Microsoft core fonts prevents font substitution and formatting errors when opening Microsoft Office documents, spreadsheets, and complex PDFs.

Install the font installer package:

```bash
sudo apt update
sudo apt install -y ttf-mscorefonts-installer

```

During package unpacking, an EULA prompt will appear:

* Press `Tab` to navigate to **`<Ok>`**, then press `Enter`.
* Use the arrow keys or `Tab` to select **`<Yes>`**, then press `Enter`.

Rebuild the system font cache:

```bash
sudo fc-cache -f -v

```

Verify that the fonts are registered:

```bash
fc-list | grep -iE "arial|times new roman|courier new"

```

---

## 7. Parallel Script Execution with pexec

`pexec` executes commands or shell scripts concurrently across multiple arguments, CPU cores, or remote nodes to optimize batch processing.

Install the package:

```bash
sudo apt update
sudo apt install -y pexec

```

### Usage Examples

Process entries sequentially from an input file using multiple execution threads:

```bash
# Run a shell command in parallel for each record in a list
pexec -l file_list.txt -c "your-command {}"

# Batch-convert images across local cores
pexec -l <(ls *.png) -c "convert {} {}.jpg"

```

Inspect command-line switches and parameters:

```bash
man pexec

```

> **Note:** If `pexec` is unavailable in your package repositories, `parallel` (`sudo apt install parallel`) or `xargs -P` provide equivalent functionality.

---

## 8. UEFI Boot Management with rEFInd

rEFInd is an EFI boot manager that dynamically detects installed operating system kernels and boot stubs without requiring manual configuration rebuilds whenever kernels change.

### 8.1 Installation

Install the package directly:

```bash
sudo apt update
sudo apt install -y refind

```

If the package is not indexed in your base distribution repositories, use the official PPA:

```bash
sudo add-apt-repository ppa:rodsmith/refind -y
sudo apt update
sudo apt install -y refind

```

### 8.2 Write EFI Stubs

Commit the bootloader files to the active EFI System Partition (ESP):

```bash
sudo refind-install

```

Confirm that the UEFI firmware has registered the boot entry:

```bash
efibootmgr -v

```

Look for an entry labelled `rEFInd Boot Manager`.

### 8.3 Post-Install Configuration

Primary configuration files are located at `/boot/efi/EFI/refind/refind.conf` or `/boot/refind.conf`.

Adjust parameters such as the countdown timeout:

```text
timeout 5

```

Reboot the system to access the graphical boot screen. If the interface does not load automatically, enter your system firmware setup (using keys such as `F12`, `F9`, or `Esc` during POST) and set `rEFInd Boot Manager` as your primary boot device.

---

## 9. Customize GRUB with GRUB Customizer

GRUB Customizer is a graphical utility that modifies bootloader parameters, menu sequences, timeout intervals, and visual themes without requiring direct edits to `/etc/default/grub`.

Add the PPA and install the software:

```bash
sudo add-apt-repository ppa:danielrichter2007/grub-customizer -y
sudo apt update
sudo apt install -y grub-customizer

```

Launch the interface from your system menu or via the terminal:

```bash
grub-customizer

```

Common administrative tasks include:

* Reordering kernel stubs and secondary operating systems.
* Renaming boot menu entries.
* Adjusting default boot targets and display timeouts.
* Configuring kernel display resolutions.

> **Caution:** Always click **Save** before closing the interface to regenerate `/boot/grub/grub.cfg`. Ensure functional recovery media is available before modifying boot configurations.

---

## 10. Completely Remove Firefox, Thunderbird, and Locale Files

On certain restricted institutional or government networks (such as NIC-GOV), Mozilla update and telemetry endpoints may experience network throttling or CDN routing failures. Removing Mozilla products avoids stalled package updates.

### 10.1 Purge Packages and System Dependencies

Completely remove the core packages, dependencies, and all associated regional language packs:

```bash
# Purge binaries, dependencies, and locale files
sudo apt purge -y firefox firefox-locale-en firefox-locale-* \
               thunderbird thunderbird-locale-en thunderbird-locale-*

# Remove orphaned dependencies and clear package caches
sudo apt autoremove -y
sudo apt autoclean

```

### 10.2 Remove Local User Profiles

To delete user profile directories, history, cached files, and local mailbox data, remove the user configurations:

```bash
rm -rf ~/.mozilla
rm -rf ~/.thunderbird

```

> **Warning:** This step permanently deletes local browser bookmarks, saved passwords, sessions, and Thunderbird email archives stored on the local drive. Back up any critical data before proceeding.

### 10.3 Verify System State

Ensure that no residual packages remain:

```bash
dpkg -l | grep -E "firefox|thunderbird"

```

---

## 11. Automated Maintenance Script: Remove Mozilla Artifacts

Save the following shell script as `remove-mozilla.sh` to automate the cleanup:

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== Purging Firefox, Thunderbird, and associated locale packs ==="
sudo apt purge -y firefox firefox-locale-en firefox-locale-* \
               thunderbird thunderbird-locale-en thunderbird-locale-*

echo "=== Removing orphaned packages and cleaning caches ==="
sudo apt autoremove -y
sudo apt autoclean

echo "=== User Profile Removal ==="
read -rp "Permanently delete ~/.mozilla and ~/.thunderbird directories? [y/N]: " confirmation
if [[ "$confirmation" =~ ^[Yy]$ ]]; then
    rm -rf "$HOME/.mozilla"
    rm -rf "$HOME/.thunderbird"
    echo "User profiles successfully deleted."
else
    echo "User profile directories preserved."
fi

echo "=== Verification ==="
dpkg -l | grep -E "firefox|thunderbird" || echo "System is completely free of Mozilla packages."

```

Make the script executable and run it:

```bash
chmod +x remove-mozilla.sh
./remove-mozilla.sh

```

---

## 12. Automated Post-Installation Pipeline

For a streamlined deployment on fresh Linux Mint XFCE installations, execute this composite workflow:

```bash
# 1. Update package lists and base system
sudo apt update && sudo apt upgrade -y && sudo apt autoremove -y

# 2. Configure baseline UFW security
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw --force enable

# 3. Deploy printing subsystem
sudo apt install -y cups cups-client hplip hplip-gui
sudo systemctl enable --now cups

# 4. Install typography assets
sudo apt install -y ttf-mscorefonts-installer
sudo fc-cache -f -v

# 5. Install parallel automation tools
sudo apt install -y pexec

# 6. Install alternative UEFI bootloader
sudo apt install -y refind
sudo refind-install

# 7. Purge problematic Mozilla applications
sudo apt purge -y firefox firefox-locale-en firefox-locale-* \
               thunderbird thunderbird-locale-en thunderbird-locale-*
sudo apt autoremove -y
rm -rf "$HOME/.mozilla" "$HOME/.thunderbird"

```

---

## References

1. [Switching Desktop Environments on Ubuntu and Linux Mint](https://oneuptime.com/blog/post/2026-03-02-switch-between-desktop-environments-ubuntu/view)
2. [Install Opera Browser on Linux Mint](https://computingforgeeks.com/install-opera-web-browser-on-linux-mint/)
3. [Brave Browser Linux Installation Documentation](https://brave.com/origin/linux/)
4. [Installing Chromium on Ubuntu and Linux Mint](https://computingforgeeks.com/install-chromium-ubuntu-linux-mint-debian/)
5. [VSCodium Installation Procedures](https://computingforgeeks.com/install-vscodium-on-ubuntudebianlinux-mint/)
6. [UFW Firewall Administration Guide](https://cloudhousetechnologies.com/blog/linux-mint-ufw-firewall-setup-guide-2026)
7. [Ubuntu Server Guide: Network Firewalls](https://ubuntu.com/server/docs/how-to/security/firewalls/)
8. [Resolving Linux Mint Printer Issues and HPLIP](https://cloudhousetechnologies.com/blog/how-to-fix-printer-not-working-linux-mint-2026)
9. [CUPS Printing Configuration Guide](https://whizz-tech.com/support/linux-printer-setup-cups-ubuntu-fedora/)
10. [TrueType Core Fonts Installation on Linux Mint](https://linuxcapable.com/how-to-install-microsoft-fonts-on-linux-mint/)
11. [Parallel Task Execution with pexec](https://www.scribd.com/document/998056986/Python3-Linux-Mint)
12. [rEFInd Boot Manager Configuration Overview](https://www.pistack.xyz/posts/2026-05-23-linux-bootloader-management-grub-vs-systemd-boot-vs-refind-guide/)
13. [GRUB Customizer Installation and Management](https://linuxcapable.com/how-to-install-grub-customizer-on-linux-mint/)
14. [Purging Applications via APT on Debian Systems](https://www.tutorialspoint.com/article/how-to-use-the-apt-get-command-in-linux)
