---
title: "Optimizing Manjaro Linux for an Intel Pentium G620 Workstation"
date: "2026-11-16"
categories: ["Linux", "System Administration"]
tags: ["manjaro", "performance-tuning", "xfce", "pentium-g620"]
description: "A targeted guide to optimizing memory, storage, and desktop performance for an Intel Pentium G620 running Manjaro Linux."
---

# Optimizing Manjaro Linux for an Intel Pentium G620 Workstation

Revitalizing an older office workstation with an Intel Pentium G620 and 6 GB of RAM requires specific tuning to prevent bottlenecks. This guide covers hardware-specific optimizations for a 2-thread Sandy Bridge processor, including low-overhead swap configuration, native NTFS mounting, and desktop environment adjustments.

## 1. Automounting the NTFS Data Partition

The target NTFS data partition is `/dev/sda4` with UUID `351095A642490756`. To ensure permanent read and write access, configure `/etc/fstab` using the native kernel `ntfs3` driver. This reduces CPU overhead on a 2-thread processor compared to the user-space `ntfs-3g` FUSE driver.

Install `ntfs-3g` as a fallback and create the mount directory:

```bash
sudo pacman -Syu ntfs-3g
sudo mkdir -p /mnt/Data
```

Back up `/etc/fstab` and open it for editing:

```bash
sudo cp /etc/fstab /etc/fstab.bak
sudo nano /etc/fstab
```

Add the following line at the bottom of `/etc/fstab`. This assumes the primary user has `uid=1000` and `gid=1000`:

```text
UUID=351095A642490756  /mnt/Data  ntfs3  uid=1000,gid=1000,dmask=022,fmask=133,windows_names,nofail  0  0
```

Reload systemd and test the mount immediately:

```bash
sudo systemctl daemon-reload
sudo mount -a
```

Verify the mount and write permissions:

```bash
lsblk -f /dev/sda4
touch /mnt/Data/test && rm /mnt/Data/test
```

## 2. Symlinking Home Folders to the Data Partition

Redirect standard user folders to the NTFS partition to keep the root filesystem lean and share files directly with Windows.

Create the target directories and migrate existing files:

```bash
mkdir -p /mnt/Data/{Documents,Downloads,Music,Pictures,Videos}

for dir in Documents Downloads Music Pictures Videos; do
    mv -n ~/"$dir"/* /mnt/Data/"$dir"/ 2>/dev/null
    rm -rf ~/"$dir"
    ln -s /mnt/Data/"$dir" ~/"$dir"
done

xdg-user-dirs-update
```

Verify the symlinks:

```bash
ls -ld ~/Documents ~/Downloads ~/Pictures
```

## 3. Configuring zram Swap for a 2-Thread CPU

The Intel Pentium G620 has only 2 hardware threads. Using `zstd` compression for `zram` can bottleneck the CPU. Instead, use the `lz4` algorithm, which requires minimal CPU cycles while effectively expanding the 5.7 GiB of physical RAM into approximately 8.5 to 9 GiB of working memory.

Install the systemd generator:

```bash
sudo pacman -S zram-generator
```

Create the configuration file at `/etc/systemd/zram-generator.conf`:

```ini
[zram0]
zram-size = 4096
compression-algorithm = lz4
swap-priority = 100
```

Activate the swap immediately:

```bash
sudo systemctl daemon-reload
sudo systemctl start /dev/zram0
```

Verify the active swap:

```bash
free -h
```

## 4. Preventing System Lockups with earlyoom and sysctl

With only 2 CPU threads, an out-of-memory stall or heavy disk flush will quickly freeze the desktop environment.

Install and configure `earlyoom` to terminate heavy processes before the system locks up:

```bash
sudo pacman -S earlyoom
sudo nano /etc/default/earlyoom
```

Set the arguments to trigger at 5% free RAM and 10% free swap:

```bash
EARLYOOM_ARGS="-r 60 -m 5 -s 10 --avoid '(^|/)(init|systemd|Xorg|sshd|xfwm4)$' --prefer '(^|/)(firefox|chromium|chrome|java)$'"
```

Enable the service:

```bash
sudo systemctl enable --now earlyoom
```

Apply low-latency virtual memory limits by creating `/etc/sysctl.d/99-desktop-perf.conf`:

```ini
vm.swappiness = 100
vm.vfs_cache_pressure = 50
vm.dirty_background_bytes = 33554432
vm.dirty_bytes = 134217728
vm.page-cluster = 0
```

Apply the changes:

```bash
sudo sysctl --system
```

Verify the settings:

```bash
sysctl vm.swappiness
systemctl is-active earlyoom
```

## 5. Hardware-Specific Tweaks for Sandy Bridge

The Intel HD Graphics 2000 integrated GPU lacks modern shader performance. Disable XFCE compositing to eliminate screen-tearing overhead and ensure instant window rendering.

Navigate to Settings, then Window Manager Tweaks, then Compositor, and uncheck Enable display compositing.

## 6. Automated Setup Command

For a clean installation, execute the following single-line command. It installs the required packages, configures `zram` with `lz4`, tunes `sysctl`, sets up `earlyoom`, mounts `/dev/sda4` using `ntfs3`, and symlinks the home folders.

```bash
sudo pacman -S --noconfirm zram-generator earlyoom ntfs-3g && printf "[zram0]\nzram-size = 4096\ncompression-algorithm = lz4\nswap-priority = 100\n" | sudo tee /etc/systemd/zram-generator.conf > /dev/null && printf "vm.swappiness = 100\nvm.vfs_cache_pressure = 50\nvm.dirty_background_bytes = 33554432\nvm.dirty_bytes = 134217728\nvm.page-cluster = 0\n" | sudo tee /etc/sysctl.d/99-desktop-perf.conf > /dev/null && printf "EARLYOOM_ARGS=\"-r 60 -m 5 -s 10 --avoid '(^|/)(init|systemd|Xorg|sshd|xfwm4)$' --prefer '(^|/)(firefox|chromium|chrome|java)$'\"\n" | sudo tee /etc/default/earlyoom > /dev/null && sudo sysctl --system && sudo systemctl daemon-reload && sudo systemctl start /dev/zram0 && sudo systemctl enable --now earlyoom && sudo mkdir -p /mnt/Data && sudo cp /etc/fstab /etc/fstab.bak && grep -q "351095A642490756" /etc/fstab || echo "UUID=351095A642490756  /mnt/Data  ntfs3  uid=$(id -u),gid=$(id -g),dmask=022,fmask=133,windows_names,nofail  0  0" | sudo tee -a /etc/fstab > /dev/null && sudo mount -a && mkdir -p /mnt/Data/{Documents,Downloads,Music,Pictures,Videos} && for d in Documents Downloads Music Pictures Videos; do [ ! -L ~/"$d" ] && mv -n ~/"$d"/* /mnt/Data/"$d"/ 2>/dev/null; rm -rf ~/"$d" && ln -s /mnt/Data/"$d" ~/"$d"; done && xdg-user-dirs-update
```

> Warning: Before executing this command, verify the UUID of `/dev/sda4`. If the first character is `B` instead of `3`, update the UUID in the command accordingly. Additionally, ensure Windows Fast Startup is disabled if the partition is shared, otherwise the mount will fail or default to read-only.

## 7. Final Verification

Run the following command to confirm all configurations are active:

```bash
free -h && findmnt /mnt/Data && ls -ld ~/Documents ~/Downloads ~/Pictures
```

The output should show 4.0 Gi of swap, `/mnt/Data` mounted as `ntfs3` with read-write permissions, and the home directories pointing directly to `/mnt/Data/`.

## References
Manjaro Linux Wiki
https://wiki.manjaro.org/