---
title: "The Ultimate Guide to Configuring Manjaro Xfce"
description: "Optimize storage, memory management, and aesthetics for a high-performance Manjaro Xfce workstation."
date: 2026-11-17 12:30:00 +0000
categories: [Linux, Desktop Customization]
tags: [manjaro, xfce, ntfs, zram, themes]
---

# The Ultimate Guide to Configuring Manjaro Xfce

Manjaro Xfce offers a lightweight foundation, but tailored configuration unlocks its full potential. This guide covers storage optimization, advanced memory management, and modern aesthetic customization to transform your daily driver.

## Taming Storage: Fixing NTFS Mounts and Symlinking User Folders

Proper handling of NTFS partitions and user directory structures ensures data accessibility and keeps the root partition lean.

### Resolving Mount Failures with `ntfs-3g`

While modern kernels include the `ntfs3` driver, `ntfs-3g` provides robust userspace compatibility for complex permissions. Install the package to ensure reliable mounting:

```bash
sudo pacman -S ntfs-3g
```

Configure `/etc/fstab` using `ntfs-3g` to map UIDs and GIDs correctly, preventing permission errors on shared data drives.

### Migrating and Symlinking User Directories

Relocate standard user directories to a large data partition and create symbolic links in your home directory. This preserves application paths while freeing up SSD space.

Execute the following script to migrate existing data and create links:

```bash
mkdir -p /mnt/Data/{Documents,Downloads,Music,Pictures,Videos,Projects,Public,Templates}

for dir in Documents Downloads Music Pictures Videos Projects Public Templates; do
    if [[ -d ~/"$dir" && ! -L ~/"$dir" ]]; then
        cp -a ~/"$dir"/. /mnt/Data/"$dir"/ 2>/dev/null
        rm -rf ~/"$dir"
        ln -s /mnt/Data/"$dir" ~/"$dir"
    elif [[ ! -e ~/"$dir" ]]; then
        ln -s /mnt/Data/"$dir" ~/"$dir"
    fi
done

xdg-user-dirs-update
```

> **Note:** Ensure `/mnt/Data` is mounted before running this script to avoid linking to empty directories.

## Supercharging Memory Management: Swap Files and Zram

Combining disk swap with compressed RAM (`zram`) prevents OOM crashes while maintaining system responsiveness under heavy loads.

### Allocating a Disk Swapfile

Create a 4GB swapfile as a safety net for hibernation or extreme memory pressure:

```bash
sudo dd if=/dev/zero of=/swapfile bs=1M count=4096 status=progress
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap defaults,pri=10 0 0' | sudo tee -a /etc/fstab
```

### Deploying Zram for Compressed RAM Swap

`zram` uses CPU cycles to compress memory pages, keeping them in RAM instead of writing to disk.

1. Load the module and configure auto-loading:

```bash
sudo modprobe zram
echo 'zram' | sudo tee /etc/modules-load.d/zram.conf
echo 'options zram num_devices=1' | sudo tee /etc/modprobe.d/zram.conf
```

2. Set up udev rules to initialize a 2GB compressed swap device with high priority:

```bash
echo 'KERNEL=="zram0", ATTR{disksize}="2G", RUN="/usr/bin/mkswap /dev/zram0", TAG+="systemd"' | sudo tee /etc/udev/rules.d/99-zram.rules
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=block
```

3. Maximize swappiness to favor compressed RAM over disk swap:

```bash
echo 'vm.swappiness=100' | sudo tee /etc/sysctl.d/99-swappiness.conf
sudo sysctl --system
```

## Polishing the Interface: Themes, Docklike Plugin, and Browsers

Xfce’s modular architecture allows for significant visual transformations without sacrificing performance.

- **Modern Taskbar**: Install `xfce4-docklike-plugin` to replace traditional window buttons with a clean, app-centric dock similar to Windows 11 or macOS.
- **Custom Themes**: Use `sassc`, `git`, and `gtk-murrine-engine` to deploy GTK themes like **Fluent** (Windows aesthetic) or **WhiteSur** (macOS aesthetic).
- **Software Ecosystem**: Install secondary browsers like Opera via the AUR (`pamac install opera`) for proprietary media codec support.

## Summary

- Use `ntfs-3g` for reliable NTFS mounts and symlink user directories to keep the root partition small.
- Combine a 4GB disk swapfile with 2GB `zram` compression for optimal memory management.
- Enhance the desktop experience with `xfce4-docklike-plugin` and modern GTK themes.
- Configure `vm.swappiness=100` to prioritize fast compressed RAM over slower disk swap.

## References

- [Arch Wiki: Swap](https://wiki.archlinux.org/title/Swap)
- [Arch Wiki: Zram](https://wiki.archlinux.org/title/Zram)
- [Xfce Documentation](https://docs.xfce.org/)