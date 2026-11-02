---
title: "Distro-Hopping Without the Collapse: Migrating Linux Mint to Manjaro Alongside Windows 11"
date: "2026-11-02"
categories: ["Linux", "System Administration"]
tags: ["Manjaro", "Windows 11", "Dual Boot", "XFCE"]
description: "A practical guide to migrating from Linux Mint to Manjaro in a dual-boot setup with Windows 11, covering bootloader recovery, memory tuning, and UI customization."
---

# Distro-Hopping Without the Collapse: The Real-World Guide to Migrating Linux Mint to Manjaro Alongside Windows 11

Distro-hopping looks clean on paper. You flash an ISO, shrink a partition, install a fresh base, and boot right into a shiny new environment. But real-world hardware, especially modern hybrid laptops running an NVIDIA GPU paired with Intel silicon, UEFI firmware, and a shared Windows 11 NTFS storage drive, has a way of humbling even seasoned tinkerers.

If you have ever stared at a missing Windows bootloader, an unmountable NTFS drive with a dirty bit error, or a desktop flooded with broken symlinks, you know how quickly an afternoon project turns into an emergency rescue session.

Here is the operational breakdown of how to migrate cleanly from Linux Mint to Manjaro XFCE, recover from bootloader missteps, optimize memory and kernel subsystems, customize the UI into a responsive Windows 11 layout, and bridge storage across partitions.

## 1. The Migration Trap: Partitioning and Bootloader Recovery

When replacing Linux Mint with Manjaro in a dual-boot setup, automated installer tools can wipe vital configurations. A dual-boot UEFI setup shares an EFI System Partition (ESP), a small FAT32 volume (usually 100 MB to 512 MB) that houses the boot configurations for both Windows (`bootmgfw.efi`) and your existing Linux kernel.

### Manual Partitioning Rules

In the Calamares installer, choosing Manual Partitioning is the safest approach:

- **The Root Partition (`/`):** Select your previous Linux Mint partition, choose your filesystem (`ext4` or `btrfs`), and flag it to format.
- **The Shared Data Drive:** Leave your NTFS partitions alone. Do not format or assign mount points during installation.
- **The EFI Partition:** Mount this existing FAT32 volume to `/boot/efi` (or `/boot`). Never select Format. Formatting the ESP wipes the Windows Boot Manager, leaving Windows unreachable.

### Troubleshooting Missing Windows in GRUB

If Manjaro installs fine but boots straight into Linux without offering Windows, GRUB simply failed to run its detection tool. Arch and Manjaro disable `os-prober` by default for security:

```bash
# Install prober and filesystem drivers
sudo pacman -S --needed os-prober ntfs-3g

# Enable probing in GRUB defaults
sudo sed -i 's/#GRUB_DISABLE_OS_PROBER=false/GRUB_DISABLE_OS_PROBER=false/' /etc/default/grub
grep -q "GRUB_DISABLE_OS_PROBER=false" /etc/default/grub || echo "GRUB_DISABLE_OS_PROBER=false" | sudo tee -a /etc/default/grub

# Rebuild the GRUB configuration
sudo update-grub
```

If GRUB remains finicky or drops entries after kernel updates, rEFInd provides a resilient alternative. Unlike GRUB, it probes UEFI stubs dynamically on every startup:

```bash
sudo pacman -S refind
sudo refind-install
```

### Worst-Case Scenario: Rebuilding a Formatted Windows EFI

If the ESP was accidentally formatted, `os-prober` will not find Windows because `\EFI\Microsoft\Boot\` is gone. Your Windows installation and personal files on `C:` remain safe; only the startup pointers are missing.

Boot into a Windows PE environment (such as a Windows 11 install thumb drive or Hiren’s BootCD PE) and open Command Prompt:

```cmd
:: 1. Launch Diskpart to inspect volumes
diskpart
list volume

:: 2. Identify the FAT32 volume (ESP) and Windows OS volume, then assign drive letters
select volume <ESP_VOLUME_NUMBER>
assign letter=S:

select volume <WINDOWS_OS_VOLUME_NUMBER>
assign letter=C:
exit

:: 3. Rebuild the BCD store and UEFI boot files from scratch
bcdboot C:\Windows /s S: /f UEFI
```

Once you see `Boot files successfully created.`, reboot into Manjaro and re-run `sudo update-grub` or `sudo refind-install` to bring both operating systems back into harmony.

## 2. Kernel and Memory Tuning: The Hybrid Swap Architecture

On modern systems with 16 GB of RAM, letting the kernel thrash a traditional, slow swap partition causes micro-stutters. A hybrid swap setup combines zRAM (fast, compressed memory blocks) with a fallback disk swapfile (a low-priority safety net).

### The Architecture

- **zRAM (Priority 100):** Compresses inactive memory pages on the fly using the `zstd` algorithm directly in RAM at a roughly 3:1 ratio.
- **Disk Swapfile (Priority 10):** Sits completely unused until physical memory and zRAM are completely exhausted, preventing out-of-memory kernel panics.

### Production One-Liner

This single-line command sets up an 8 GB fallback swapfile, provisions zRAM via `systemd-zram-generator`, tunes virtual memory cache pressures, and enables TRIM maintenance timers:

```bash
sudo swapoff -a && sudo fallocate -l 8G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon -p 10 /swapfile && grep -qxF '/swapfile none swap defaults,pri=10 0 0' /etc/fstab || echo '/swapfile none swap defaults,pri=10 0 0' | sudo tee -a /etc/fstab && sudo pacman -S --needed --noconfirm zram-generator pacman-contrib && printf '[zram0]\nzram-size = ram\ncompression-algorithm = zstd\nswap-priority = 100\nfs-type = swap\n' | sudo tee /etc/systemd/zram-generator.conf && printf 'vm.swappiness = 100\nvm.vfs_cache_pressure = 50\nvm.dirty_background_ratio = 5\nvm.dirty_ratio = 10\n' | sudo tee /etc/sysctl.d/99-performance.conf && sudo sysctl --system && sudo systemctl daemon-reload && sudo systemctl start systemd-zram-setup@zram0.service && sudo systemctl enable --now fstrim.timer paccache.timer && swapon --show && zramctl
```

## 3. Resolving the Failed to Mount NTFS Hurdle

When accessing your shared NTFS partition (e.g., `/dev/nvme0n1p4`), file managers like Thunar often throw a roadblock:

> `Error mounting /dev/nvme0n1p4 ... wrong fs type, bad option, bad superblock on /dev/nvme0n1p4, missing codepage or helper program, or other error`

### Why This Happens

1. **Windows Fast Startup and Hybrid Sleep:** Windows 11 hibernates kernel state during shutdowns, marking NTFS volumes as dirty to prevent external changes from corrupting the filesystem.
2. **Missing Maintenance Binaries:** Arch-based distributions separate core drivers from utility programs. While `ntfs-3g` handles standard mounting, tools like `ntfsfix` reside inside the `ntfsprogs` package.

### The Fix

To clear the lock without touching your stored data:

```bash
# 1. Install maintenance binaries
sudo pacman -S --needed ntfsprogs

# 2. Reset the dirty hibernation flag
sudo ntfsfix -d /dev/nvme0n1p4
```

Alternatively, mount the drive using the Linux kernel in-tree `ntfs3` driver with the force flag:

```bash
sudo mkdir -p /mnt/new
sudo mount -t ntfs3 -o rw,force,uid=1000,gid=1000 /dev/nvme0n1p4 /mnt/new
```

### Making Mounts Permanent in /etc/fstab

To ensure the drive mounts automatically on boot without stalling the startup sequence if the drive is slow to initialize:

```bash
UUID=$(sudo blkid -s UUID -o value /dev/nvme0n1p4) && echo "UUID=$UUID /mnt/new ntfs3 rw,force,uid=1000,gid=1000,nofail 0 0" | sudo tee -a /etc/fstab
```

## 4. Cross-OS Storage Symlinking and Avoiding the Recursive Trap

The goal of a shared NTFS partition is simple: have your Linux home folders (`Documents`, `Downloads`, `Music`, etc.) point directly to your shared drive so you do not juggle two sets of personal files.

However, three common issues often derail this process:

### Issue A: Zsh Pattern Errors

Manjaro ships with Zsh by default. When you paste multi-line shell scripts containing inline `#` comments, Zsh interprets `#` as an extended globbing wildcard rather than a comment indicator.

- **The Permanent Fix:** Add `setopt INTERACTIVE_COMMENTS` to your `~/.zshrc`.

### Issue B: Circular Recursive Links

If you run `ln -s /mnt/new/Documents ~/Documents` while `~/Documents` already exists as an active directory or previous link, `ln` creates a nested shortcut inside the folder, creating an infinite loop. Always use `ln -sfn` to replace destinations cleanly.

### Issue C: The XDG Desktop Dilemma

If your `~/.config/user-dirs.dirs` configuration sets `XDG_DOCUMENTS_DIR="$HOME/"`, the XFCE desktop manager assumes your entire home folder is a target directory. Every symlink in `~` gets painted across your desktop surface. Deleting an icon from the desktop deletes the symlink straight out of your home directory.

Furthermore, symlinking `~/Desktop` directly to an NTFS volume often leads to boot race conditions. If the drive mounts a second after login, the desktop manager fails to locate the desktop directory, dropping desktop icons and reverting wallpapers.

### The Clean Solution

1. **Lock XDG Configurations:** Ensure paths point to discrete folders and prevent automatic overrides:

```bash
cat << 'EOF' > ~/.config/user-dirs.dirs
XDG_DESKTOP_DIR="$HOME/Desktop"
XDG_DOWNLOAD_DIR="$HOME/Downloads"
XDG_TEMPLATES_DIR="$HOME/Templates"
XDG_PUBLICSHARE_DIR="$HOME/Public"
XDG_DOCUMENTS_DIR="$HOME/Documents"
XDG_MUSIC_DIR="$HOME/Music"
XDG_PICTURES_DIR="$HOME/Pictures"
XDG_VIDEOS_DIR="$HOME/Videos"
XDG_PROJECTS_DIR="$HOME/Projects"
EOF
echo "enabled=False" > ~/.config/user-dirs.conf
```

2. **Clean, Link, and Refresh:** Run this single pipeline to clean nested links, preserve local `~/Desktop`, migrate existing files, link data folders to `/mnt/new`, and reload the desktop:

```bash
for d in Documents Downloads Music Pictures Videos Projects Public Templates; do [ -L "/mnt/new/$d/$d" ] && rm -v "/mnt/new/$d/$d"; mkdir -p "/mnt/new/$d" && [ -d "$HOME/$d" ] && [ ! -L "$HOME/$d" ] && cp -a "$HOME/$d/." "/mnt/new/$d/" 2>/dev/null; rm -rf "$HOME/$d"; ln -sfn "/mnt/new/$d" "$HOME/$d"; done && mkdir -p "$HOME/Desktop" && xdg-user-dirs-update && xfdesktop --reload
```

## 5. Laptop Hardware Stability: NVIDIA and Intel Wi-Fi

Hybrid graphics laptops (Intel CPU plus discrete NVIDIA GPU) frequently suffer from Wi-Fi dropouts on Linux when using open-source `nouveau` drivers.

### Why Proprietary Drivers Fix Wi-Fi

Nouveau often fails to negotiate PCIe Active State Power Management (ASPM) cleanly. Because the discrete GPU and the Intel Wi-Fi card share the same PCIe root complex, unhandled interrupts flood the bus, causing the wireless card to stall or disconnect.

Switching to the proprietary `nvidia` driver enables full runtime power management, stabilizing PCIe signaling.

### Locking Down Hardware Stability

1. **Ensure the Persistence Daemon Runs:**

```bash
sudo systemctl enable --now nvidia-persistenced.service
```

2. **Prevent Intel Wi-Fi Sleep Drops:** Prevent the wireless module from entering unstable aggressive power-saving states:

```bash
echo "options iwlwifi power_save=0" | sudo tee /etc/modprobe.d/iwlwifi.conf
echo "options iwlmvm power_scheme=1" | sudo tee -a /etc/modprobe.d/iwlwifi.conf
```

3. **Blacklist Residual Nouveau Modules:**

```bash
cat << 'EOF' | sudo tee /etc/modprobe.d/nouveau-blacklist.conf
blacklist nouveau
options nouveau modeset=0
EOF
sudo mkinitcpio -P
```

## 6. Transforming XFCE into a Windows 11 Workflow

XFCE is lightweight, but out-of-the-box it feels retro. With a few targeted packages and panel tweaks, you can replicate the modern, centered, rounded aesthetic of Windows 11 Fluent Design without the background bloat.

### Panel and Docklike Taskbar Setup

- **Install Plugins:**

```bash
sudo pacman -S --needed xfce4-docklike-plugin xfce4-netload-plugin
```

- **Panel Configuration:**
  1. Open Panel Preferences.
  2. Drag the panel to the bottom edge, uncheck Lock Panel, and set row size to 48px.
  3. Under the Items tab:
     - Remove the legacy Window Buttons.
     - Add Docklike Taskbar to group open windows by application icons and allow pinning.
     - Add the Network Monitor to the system tray for real-time bandwidth metrics.
     - To center the taskbar: Add a Separator before the dock and another Separator after it. Set both separators to Transparent and check Expand. This pushes the Start menu and Docklike icons directly into the center of the screen.

### Fluent Themes and Styling

Install the modern theme components:

```bash
pamac build --no-confirm fluent-gtk-theme fluent-icon-theme bibata-cursor-theme
```

- **Window Style:** Under Appearance -> Style, select `Fluent-dark`.
- **Window Borders:** Under Window Manager -> Style, select `Fluent-dark` for rounded title bars.
- **Icons and Cursors:** Apply `Fluent-dark` icons and `Bibata-Modern-Classic` cursors.

### Window Tiling and Snapping

While XFCE does not ship with dynamic automatic tiling by default:

- **Edge Snapping:** Open Window Manager Tweaks -> Accessibility -> Check Automatically tile windows when moving toward the screen edge.
- **Keyboard Shortcuts:** Open Window Manager -> Keyboard tab. Bind Tile window to the left to `Super + Left` and Tile window to the right to `Super + Right` to replicate Windows Snap shortcuts.

## Summary Checklist

| Objective | Key Tool and Configuration | Primary Command and Setting |
| --- | --- | --- |
| Boot Repair | `bcdboot` and `rEFInd` | `bcdboot C:\Windows /s S: /f UEFI` |
| Memory Optimization | `zram-generator` and `swapfile` | Priority 100 on zRAM, Priority 10 on fallback file |
| NTFS Mounting | `ntfsprogs` and `ntfs3` | `sudo ntfsfix -d /dev/nvme0n1p4` |
| Cross-OS Symlinks | Shell loops and `ln -sfn` | Bind data folders to `/mnt/new`, keep `~/Desktop` local |
| Shell Pasting | Zsh interactive comments | `setopt INTERACTIVE_COMMENTS` in `~/.zshrc` |
| Hardware Stability | `nvidia-persistenced` and `iwlwifi` | Disable Wi-Fi sleep, blacklist nouveau |
| Desktop UI | Fluent GTK and Docklike Plugin | Centered bottom panel with expanding separators |

## References
Manjaro Wiki
https://wiki.manjaro.org/
Arch Wiki
https://wiki.archlinux.org/
Microsoft BCDboot Command-Line Options
https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/bcdboot-command-line-options-techref