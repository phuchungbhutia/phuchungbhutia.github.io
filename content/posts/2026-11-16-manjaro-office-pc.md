---
title: "Setting Up an Older Office PC on Manjaro Linux"
date: "2026-11-16"
categories: ["Linux", "System Administration"]
tags: ["manjaro", "performance-tuning", "xfce", "office-workstation"]
description: "A comprehensive guide to optimizing and configuring an older office workstation running Manjaro Linux for daily productivity."
---

# Setting Up an Older Office PC on Manjaro Linux

Revitalizing an older office workstation, such as a 3rd-generation Intel Core i3 with 6 GB of RAM, is an excellent use case for Manjaro Linux. With targeted tweaks, an aging machine can run cool, responsive, and reliable for daily office workloads. This setup covers hardware drivers, performance tuning, desktop customization, and storage integration.

## 1. Configuring Office Networking

Office networks frequently combine internal Ethernet intranets with external Wi-Fi internet access, or rely on proprietary Realtek and Broadcom chipsets that require specific drivers.

### Check Hardware and Active Drivers

Verify that Manjaro recognizes both network interface cards and has loaded active kernel modules:

```bash
inxi -Nazy
```

Look for Device-1 and Device-2 and verify that neither lists `driver: N/A`. If your wireless card is blocked at the software level, unblock it via:

```bash
rfkill list all
rfkill unblock wifi
```

### Install Proprietary Network Drivers

Realtek Ethernet controllers often ship using the generic `r8169` driver, which can drop packets under load. Switch to the vendor-specific `r8168` driver using the Manjaro Hardware Configuration tool:

- Open Manjaro Settings Manager and navigate to Hardware Configuration, or run `manjaro-settings-manager -m msm_mhwd`.
- Check Show All Devices in the bottom-left corner.
- Right-click the recommended driver under Network controller, such as `network-r8168`, and click Install, then reboot.

### Use Office Intranet and Internet Simultaneously

If your wired LAN connects only to an internal office intranet while Wi-Fi provides internet access, stop the wired connection from hijacking the default route:

- Open Advanced Network Configuration (`nm-connection-editor`) and edit your Wired connection.
- Go to IPv4 Settings and click Routes.
- Check Use this connection only for resources on its network, save, and reconnect.
- Confirm with `ip route` that your default via gateway points to your Wi-Fi interface while internal office subnets route through Ethernet.

For offices using WPA2 or WPA3 Enterprise Wi-Fi, set Wi-Fi Security to WPA and WPA2 Enterprise, Authentication to PEAP, Inner authentication to MSCHAPv2, and enter your domain credentials.

## 2. Installing an HP LaserJet Printer

Manjaro handles HP printers cleanly through CUPS and the HP Linux Imaging and Printing stack.

Install the required packages:

```bash
sudo pacman -Syu manjaro-printer hplip python-pyqt5
```

Start the CUPS Print Server:

```bash
sudo systemctl enable --now cups.service
```

Install the proprietary binary plugin. Most HP LaserJet models require this closed-source plugin to communicate with the print engine. Build it from the AUR so it stays matched to your `hplip` release:

```bash
pamac build hplip-plugin
```

Run the interactive printer setup:

```bash
sudo hp-setup -i
```

Choose 0 for a direct USB connection or 1 for a networked printer. If auto-discovery misses a printer across an office subnet, pass its IP address directly using `sudo hp-setup -i 192.168.1.XXX`.

## 3. Syncing System Time

Accurate system time is essential for SSL certificates, network authentication, and file timestamps.

Enable automatic NTP synchronization:

```bash
sudo systemctl enable --now systemd-timesyncd.service
sudo timedatectl set-ntp true
sudo timedatectl set-timezone Asia/Kolkata
```

Verify clock status by running `timedatectl status` and looking for `System clock synchronized: yes`.

If UDP port 123 is blocked by an office firewall, point `/etc/systemd/timesyncd.conf` to regional or internal NTP servers and restart `systemd-timesyncd.service`.

If rebooting between Windows and Manjaro shifts the hardware clock, tell Manjaro to keep the hardware clock in local time:

```bash
sudo timedatectl set-local-rtc 1 --adjust-system-clock
```

## 4. Performance Optimization for Core i3 and 6 GB RAM

On a dual-core Ivy Bridge processor with 6 GB of RAM, eliminating disk swap bottlenecks and preventing memory-induced freezes makes the largest day-to-day difference.

### Configure 4 GB Compressed zram Swap

Instead of swapping to a slow mechanical drive, `zram` creates a compressed swap block directly in RAM. With 6 GB physical RAM, a 4 GB `zram` pool using `zstd` compression effectively provides 9 to 10 GB of usable working memory.

Install the systemd generator:

```bash
sudo pacman -S zram-generator
```

Create `/etc/systemd/zram-generator.conf`:

```ini
[zram0]
zram-size = 4096
compression-algorithm = zstd
swap-priority = 100
```

Activate immediately:

```bash
sudo systemctl daemon-reload
sudo systemctl start /dev/zram0
```

### Tune Kernel Virtual Memory

Create `/etc/sysctl.d/99-desktop-perf.conf` so the kernel favors compressed `zram` and keeps disk writeback queues tight for older SATA controllers:

```ini
vm.swappiness = 100
vm.vfs_cache_pressure = 50
vm.dirty_background_bytes = 33554432
vm.dirty_bytes = 134217728
vm.page-cluster = 0
```

Apply the changes with `sudo sysctl --system`.

### Prevent System Lockups with earlyoom

If a runaway browser tab exhausts both physical RAM and `zram`, `earlyoom` terminates the heaviest offending process before the desktop freezes:

```bash
sudo pacman -S earlyoom
```

Configure `/etc/default/earlyoom` to trigger at 5% free RAM and 10% free swap:

```bash
EARLYOOM_ARGS="-r 60 -m 5 -s 10 --avoid '(^|/)(init|systemd|Xorg|sshd|xfwm4|kwin_x11)$' --prefer '(^|/)(firefox|chromium|chrome|java)$'"
```

Enable it with `sudo systemctl enable --now earlyoom`.

### Ivy Bridge CPU and App Tweaks

- Intel Microcode and Hardware Video Decoding: Offload video playback from the dual-core CPU to integrated Intel HD graphics using `sudo pacman -S intel-ucode libva-intel-driver intel-media-sdk`.
- CPU Frequency Governor: Enable `cpupower` with `schedutil` in `/etc/default/cpupower` for responsive clock scaling via `sudo systemctl enable --now cpupower.service`.
- Stick to an LTS Kernel: Use Linux 6.6 LTS or 6.12 LTS in Manjaro Settings Manager for maximum stability on older hardware.
- Firefox and LibreOffice: In Firefox `about:config`, enable `browser.tabs.unloadOnLowMemory` and lower `browser.sessionhistory.max_total_viewers` to 2. In LibreOffice, use `libreoffice-still` and disable hardware acceleration if large spreadsheets scroll sluggishly.

## 5. Customizing XFCE

XFCE can mimic either a modern Windows taskbar or a macOS dock layout using lightweight native panel plugins.

### Install Plugins and Themes

```bash
sudo pacman -Syu xfce4-goodies xfce4-docklike-plugin papirus-icon-theme arc-gtk-theme xfce4-panel-profiles
```

### Add a Live NetSpeed Monitor

- Right-click the panel, go to Panel, and select Add New Items to add Network Monitor.
- Open its Properties, enter your active network device name, switch presentation to Values, and set the update interval to 1.00 second.

### Replace Basic Window Buttons with a Modern Taskbar

- Open Panel Preferences and go to Items. Remove Window Buttons and add Docklike Taskbar.
- Right-click running apps on the taskbar and select Pin to Dock to keep them pinned.

### Choose Your Layout

- Windows Style: Move a single 38px to 40px panel to the bottom, switch Whisker Menu to icon view with category names, and apply Arc-Dark and Papirus-Dark under Settings and Appearance.
- macOS Style: Keep a slim 28px top bar for menus and system tray icons. Create a second centered bottom panel with dynamic length and 75% opacity containing only Docklike Taskbar. Move window Close, Minimize, and Maximize buttons to the left under Window Manager settings.

### Back Up Your Layout

Save your finished configuration in Panel Profiles so you can restore it anytime with one click.

## 6. Automounting an NTFS Drive and Symlinking Home Folders

Sharing a large NTFS partition between Manjaro and Windows, and redirecting Documents, Downloads, Pictures, Music, and Videos onto it, keeps your Linux root partition lean and your files accessible from both operating systems.

> Important: If dual-booting, disable Fast Startup inside Windows Power Options and perform a full shutdown. Otherwise, Windows leaves the NTFS volume locked in a hibernated state, forcing Linux to mount it read-only.

### Permanent Read and Write Mount in /etc/fstab

Install `ntfs-3g` and look up your NTFS partition UUID:

```bash
sudo pacman -Syu ntfs-3g
lsblk -f
```

Create a mount point and back up `/etc/fstab`:

```bash
sudo mkdir -p /mnt/Data
sudo cp /etc/fstab /etc/fstab.bak
```

Add your partition to `/etc/fstab` (confirm your `uid` and `gid` are 1000 via `id -u` and `id -g`):

```text
UUID=YOUR_UUID_HERE  /mnt/Data  ntfs-3g  uid=1000,gid=1000,dmask=022,fmask=133,windows_names,nofail,x-systemd.device-timeout=5  0  0
```

Alternatively, replace `ntfs-3g` with the kernel native `ntfs3` driver for slightly lower CPU overhead during large file transfers.

Mount immediately and verify write permissions:

```bash
sudo systemctl daemon-reload
sudo mount -a
```

### Redirect Home Folders to the NTFS Partition

Create matching directories on `/mnt/Data`, migrate any existing files, and replace the local home folders with symbolic links:

```bash
mkdir -p /mnt/Data/{Documents,Downloads,Music,Pictures,Videos}

for dir in Documents Downloads Music Pictures Videos; do
    mv -n ~/"$dir"/* /mnt/Data/"$dir"/ 2>/dev/null
    rm -rf ~/"$dir"
    ln -s /mnt/Data/"$dir" ~/"$dir"
done

xdg-user-dirs-update
```

Running `ls -ld ~/Documents ~/Downloads` will now show clean symlinks pointing directly to `/mnt/Data/`, directly integrating your shared drive into Thunar and all desktop applications.

## References
Manjaro Linux Documentation
https://wiki.manjaro.org/