---
title: "Configuring Manjaro Xfce for Storage, Memory, and Desktop Aesthetics"
date: "2026-11-16"
categories: ["Linux", "System Administration"]
tags: ["manjaro", "xfce", "storage", "memory-management"]
description: "A technical guide to configuring NTFS storage, memory compression, and desktop aesthetics on Manjaro Xfce."
---

# Configuring Manjaro Xfce for Storage, Memory, and Desktop Aesthetics

Setting up a Linux workstation requires precise system configuration. Manjaro Xfce provides an efficient foundation, but optimizing storage, memory management, and the desktop environment ensures a reliable daily driver. This guide details the exact steps to configure shared partitions, allocate compressed memory, and apply modern interface themes.

## Configuring NTFS Storage and User Directories

When dual-booting or utilizing large shared data drives formatted as NTFS, Linux requires careful handling of mount drivers and file permissions.

### Resolving Mount Failures

Modern Linux kernels include the in-kernel `ntfs3` driver, but it can occasionally lack the robust userspace compatibility needed for complex directory symlinking. Installing the `ntfs-3g` package utilizes the FUSE driver to ensure reliable mounting with proper UID and GID mapping:

```bash
sudo pacman -S ntfs-3g
```

Configure `/etc/fstab` with the correct mount options to ensure `/mnt/Data` mounts cleanly on every boot without permission errors.

### Migrating and Symlinking User Directories

To keep the root solid-state drive lean while utilizing a large data partition, relocate standard user directories to `/mnt/Data` and link them back to the home directory:

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

This script guarantees that desktop applications, file managers, and system shortcuts reliably recognize the relocated files.

## Configuring Swap Files and Zram

Memory management dictates system stability. Relying solely on disk swap causes stuttering under heavy load, while omitting swap risks sudden Out-Of-Memory crashes. The optimal configuration combines a traditional disk swap backup with compressed RAM.

### Allocating a Disk Swapfile

A 4 GB swapfile provides a safety net for heavy applications or hibernation:

```bash
sudo dd if=/dev/zero of=/swapfile bs=1M count=4096 status=progress
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap defaults,pri=10 0 0' | sudo tee -a /etc/fstab
```

### Deploying Zram for Compressed RAM Swap

The `zram` module creates a compressed block device in RAM, allowing the CPU to compress and store memory pages instantly without hitting physical disk storage.

Load the module and configure auto-loading:

```bash
sudo modprobe zram
echo 'zram' | sudo tee /etc/modules-load.d/zram.conf
echo 'options zram num_devices=1' | sudo tee /etc/modprobe.d/zram.conf
```

Set up udev rules to initialize a 2 GB compressed swap device with high priority:

```bash
echo 'KERNEL=="zram0", ATTR{disksize}="2G", RUN="/usr/bin/mkswap /dev/zram0", TAG+="systemd"' | sudo tee /etc/udev/rules.d/99-zram.rules
sudo udevadm control --reload-rules
sudo udevadm trigger --subsystem-match=block
```

Maximize swappiness so the kernel favors compressed RAM over disk:

```bash
echo 'vm.swappiness=100' | sudo tee /etc/sysctl.d/99-swappiness.conf
sudo sysctl --system
```

## Customizing the Desktop Environment

The modular architecture of Xfce allows for complete visual transformation without sacrificing performance.

- Modern Taskbar: Install `xfce4-docklike-plugin` to replace traditional window buttons with an application-centric dock experience.
- Custom Themes: Install build dependencies such as `sassc`, `git`, and `gtk-engine-murrine` to compile and deploy GTK themes like Fluent for a Windows aesthetic or WhiteSur for a macOS aesthetic.
- Software Ecosystem: Install secondary browsers like Opera from the Arch User Repository using `pamac build opera` to ensure compatibility with proprietary media codecs and extensions.

## References
Manjaro Linux Wiki
https://wiki.manjaro.org/