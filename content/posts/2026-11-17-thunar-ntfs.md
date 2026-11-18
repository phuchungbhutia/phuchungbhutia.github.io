---
title: "Fix Duplicate NTFS Entries and Truncated Lines in /etc/fstab"
description: "Resolve duplicate mount entries, fix truncated lines, and configure x-gvfs-show for Thunar visibility."
date: 2026-11-17 12:00:00 +0000
categories: [Linux, System Administration]
tags: [fstab, ntfs, thunar, swap, linux]
---

# Fix Duplicate NTFS Entries and Truncated Lines in /etc/fstab

Duplicate entries and truncated lines in `/etc/fstab` can cause mount failures or unexpected behavior. This guide resolves conflicts between `ntfs-3g` and `ntfs3`, fixes truncation artifacts, and ensures proper visibility in file managers like Thunar.

## Open fstab for Editing

Root privileges are required to modify system mount configurations. Use a terminal-based editor to access the file safely.

```bash
sudo nano /etc/fstab
```

The editor opens displaying your current system mount configurations. Verify that you can navigate the file before making changes.

## Replace with Clean Configuration

Remove duplicate entries for `/mnt/Data` and fix any lines ending with `>` due to truncation. Replace the entire file content with the following verified layout:

```text
# /etc/fstab: static file system information.
UUID=2AC3-9877 /boot/efi vfat umask=0077 0 2
UUID=85949b92-3bf6-41c6-a058-ea361f9668c0 / ext4 defaults 0 1
UUID=351095A642490756 /mnt/Data ntfs-3g defaults,x-gvfs-show,uid=1000,gid=1000,dmask=022,fmask=133 0 0
/swapfile none swap defaults,pri=10 0 0
```

Key configuration details:
- Uses `ntfs-3g` instead of `ntfs3` for broader compatibility
- Includes `x-gvfs-show` to ensure visibility in Thunar's sidebar
- Sets `uid=1000,gid=1000` for proper user ownership
- Configures swap priority with `pri=10`

Save the file by pressing `Ctrl + O`, hit `Enter`, then exit with `Ctrl + X`.

> **Note:** Run `cat /etc/fstab` to confirm all lines are fully written without trailing `>` characters.

## Test and Apply Mounts

Verify syntax correctness before rebooting to prevent boot failures.

```bash
sudo mount -a
```

The command should complete without any error messages. If errors occur, review the output and correct the offending line before proceeding.

Open Thunar to confirm `/mnt/Data` now appears under the left sidebar devices. The drive should be accessible with proper read/write permissions.

## Summary

- Removed duplicate NTFS entries and standardized on `ntfs-3g` driver
- Fixed truncated lines and added `x-gvfs-show` for Thunar visibility
- Configured swap file with priority `pri=10` for optimal performance
- Verified configuration with `sudo mount -a` before finalizing

## References

- [fstab(5) Man Page](https://man7.org/linux/man-pages/man5/fstab.5.html)
- [NTFS-3G Documentation](https://www.tuxera.com/community/open-source-ntfs-3g/)
- [Thunar File Manager](https://docs.xfce.org/xfce/thunar/start)