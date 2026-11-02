---
title: "Surviving the Dual-Boot Gauntlet: Cleaning GRUB, Taming UEFI NVRAM, and Fixing Broken Boot Scripts in Manjaro"
date: "2026-11-02"
categories: ["Linux", "System Administration"]
tags: ["manjaro", "grub", "uefi", "efibootmgr", "dual-boot", "arch-linux"]
description: "A field-tested procedure for undoing Grub Customizer damage, purging dead UEFI boot entries from motherboard NVRAM, and rebuilding a Manjaro and Windows 11 menu that survives kernel updates."
---

# Surviving the Dual-Boot Gauntlet: Cleaning GRUB, Taming UEFI NVRAM, and Fixing Broken Boot Scripts in Manjaro

Dual-booting Linux alongside Windows 11 is easy to install and hard to maintain. You try one distribution, replace it with another, test rEFInd for a week, and eighteen months later your motherboard firmware is an archaeological dig site: `ubuntu`, `debian`, `deepin`, `Linpus lite`, and two copies of `Windows Boot Manager`, all pointing at binaries that no longer exist.

Then a graphical tool promises to tidy the menu, injects a malformed proxy script into `/etc/grub.d/`, and `update-grub` stops writing a configuration file entirely. The system still boots — right up until a kernel update makes the stale `grub.cfg` refer to an image that has been removed.

What follows is the full recovery sequence: restore packaged GRUB scripts, purge zombie NVRAM entries safely, clean the EFI System Partition, and configure the menu the way Arch and Manjaro expect it to be configured.

## Why Grub Customizer Breaks Arch and Manjaro

Grub Customizer is built around the Debian and Ubuntu packaging model. Rather than editing `/etc/default/grub` for the settings that belong there, it rewrites the generator scripts in `/etc/grub.d/`, renames the distribution's native scripts, and inserts proxy redirectors such as `41_snapshots-btrfs_proxy` and `60_memtest86+_proxy` that source a cached copy of the menu.

On a rolling release, those cached copies rot. When `grub-btrfs`, `memtest86+`, or a snapshot hook updates underneath the proxy, the generated fragment can end up syntactically invalid.

### The empty else block

The classic failure looks like this in the generated output:

```bash
### BEGIN /etc/grub.d/41_snapshots-btrfs_proxy ###
if [ ! -e "${prefix}/grub-btrfs.cfg" ]; then
echo ""
else

fi
### END /etc/grub.d/41_snapshots-btrfs_proxy ###
```

Neither POSIX shell nor GRUB's own script parser accepts an empty `else` branch. `grub-mkconfig` runs `grub-script-check` against the candidate file before committing it, and the parser rejects the whole configuration:

```text
error: grub-core/script/lexer.c:grub_script_yyerror:352:syntax error.
error: grub-core/script/lexer.c:grub_script_yyerror:352:Incorrect command.
Syntax error at line 231
Syntax errors are detected in generated GRUB config file.
```

### What that error actually costs you

The syntax check is a safety net, not the bug. Because validation failed, `/boot/grub/grub.cfg.new` is discarded and `/boot/grub/grub.cfg` is left untouched. Your machine keeps booting the last good menu, which is why the problem often goes unnoticed for weeks — until the kernel package rotates and the old `vmlinuz` and `initramfs` referenced by that frozen menu are gone.

Fix the generator, not the generated file. Hand-editing `grub.cfg` buys you exactly one package update.

## Capture the Current State Before Changing Anything

Firmware edits are recoverable, but only if you wrote down what was there first. Boot into Manjaro normally and confirm you are running in UEFI mode, because `efibootmgr` is useless on a legacy BIOS install:

```bash
test -d /sys/firmware/efi && echo "UEFI boot confirmed"
findmnt /boot/efi
```

Now take three backups. The `tee` form matters here: `sudo efibootmgr -v > file` fails because the redirection happens in your unprivileged shell.

```bash
# Full NVRAM dump, including device paths
sudo efibootmgr -v | tee "$HOME/nvram-$(date +%F).txt"

# The generator scripts, moved out of the execution path later
sudo cp -a /etc/grub.d "$HOME/grub.d-$(date +%F)"

# The entire EFI System Partition, usually under 500 MB
sudo cp -a /boot/efi "/root/esp-backup-$(date +%F)"
```

If BitLocker is active on the Windows side, retrieve the recovery key before you touch boot order or Secure Boot state. Firmware changes to the measured boot path can trigger a recovery prompt on the next Windows start.

## Rebuild the Native GRUB Scripts

### Remove the customizer

```bash
sudo pacman -Rns grub-customizer
```

Package removal does not undo the edits it made to `/etc/grub.d/`. That directory is now yours to clean.

### Quarantine the proxy and helper scripts

Move the debris outside `/etc/grub.d/` rather than deleting it outright. Anything executable inside that directory is run by `grub-mkconfig`, so a "backup" subfolder left in place will still be parsed. Note also that `bin` and `backup` are directories, which plain `rm -f` cannot remove:

```bash
sudo mkdir -p /root/grub.d-quarantine

sudo mv /etc/grub.d/*_proxy /root/grub.d-quarantine/ 2>/dev/null

for f in 06_grub-customizer_menu_color_helper 31_efi_bootnext efi_bootnext \
         memtest86+ memtest86+-efi snapshots-btrfs bin backup; do
  sudo mv "/etc/grub.d/$f" /root/grub.d-quarantine/ 2>/dev/null
done
```

Grub Customizer also renames native scripts to suffixed clones such as `10_linux.dpkg-old` or unnumbered duplicates. List what remains and compare against the package manifest:

```bash
ls -la /etc/grub.d/
sudo pacman -Qkk grub grub-btrfs
```

`pacman -Qkk` reports every file whose size, permissions, or checksum drifts from the package database, which is the fastest way to spot a script the tool rewrote in place.

### Restore the packaged versions

Reinstall with a targeted overwrite so Pacman replaces the modified files with upstream copies:

```bash
sudo pacman -S --overwrite "/etc/grub.d/*" grub grub-btrfs
```

Scope the glob to `/etc/grub.d/*` exactly as shown. A bare `--overwrite "*"` is a different and much blunter instrument.

A healthy Manjaro directory afterwards contains only numbered generators and the README. The precise set depends on which optional packages you have installed:

```text
00_header
10_linux
15_ostree
20_linux_xen
25_bli
30_os-prober
30_uefi-firmware
40_custom
41_custom
41_snapshots-btrfs
README
```

Files such as `15_ostree`, `20_linux_xen`, and `25_bli` are harmless when their subsystems are absent; they detect that and emit nothing. What must not be present is any `*_proxy` file or unnumbered clone.

## Purge Zombie Entries from NVRAM

Deleting an operating system removes its files, not the firmware's `Boot####` variable pointing at them. Those variables live in motherboard NVRAM and survive reinstalls, disk wipes, and distribution changes.

### Read the table

```bash
sudo efibootmgr -v
```

A neglected machine returns something like this:

```text
BootCurrent: 0008
Timeout: 0 seconds
BootOrder: 0008,0007,0006,0002,0005,0000,0004,0001,2001,2002,2003
Boot0000* Windows Boot Manager    HD(1,GPT,...)/\EFI\Microsoft\Boot\bootmgfw.efi
Boot0001* Linpus lite             HD(1,GPT,...)/\EFI\Boot\grubx64.efiRC
Boot0002* rEFInd Boot Manager     HD(1,GPT,...)/\EFI\refind\refind_x64.efi
Boot0003* EFI USB Device          ...
Boot0004* deepin                  HD(1,GPT,...)/\EFI\deepin\shimx64.efi
Boot0005* Windows Boot Manager    HD(1,GPT,...)/\EFI\Microsoft\Boot\bootmgfw.efi57494...
Boot0006* debian                  HD(1,GPT,...)/\EFI\deepin\shimx64.efi
Boot0007* ubuntu                  HD(1,GPT,...)/\EFI\ubuntu\shimx64.efi
Boot0008* Manjaro                 HD(1,GPT,...)/\EFI\Manjaro\grubx64.efi
Boot2001* EFI USB Device          RC
Boot2002* EFI DVD/CDROM           RC
Boot2003* EFI Network             RC
```

`BootCurrent` is the single most important line on the screen. It identifies the entry that started the running kernel, and deleting it is how people turn a cleanup into a rescue-USB exercise.

### Decide what stays

| Slot   | Label                | Target                             | Action | Reason                              |
| ------ | -------------------- | ---------------------------------- | ------ | ----------------------------------- |
| `0008` | Manjaro              | `\EFI\Manjaro\grubx64.efi`         | Keep   | Matches `BootCurrent`               |
| `0000` | Windows Boot Manager | `\EFI\Microsoft\Boot\bootmgfw.efi` | Keep   | Clean primary Windows loader        |
| `0005` | Windows Boot Manager | `bootmgfw.efi` plus BCD blob       | Delete | Duplicate with stale BCD payload    |
| `0001` | Linpus lite          | `\EFI\Boot\grubx64.efi`            | Delete | Vendor stub, binary removed         |
| `0002` | rEFInd Boot Manager  | `\EFI\refind\refind_x64.efi`       | Delete | Abandoned bootloader                |
| `0003` | EFI USB Device       | Removable path                     | Delete | Stale one-time installer entry      |
| `0004` | deepin               | `\EFI\deepin\shimx64.efi`          | Delete | Distribution wiped                  |
| `0006` | debian               | `\EFI\deepin\shimx64.efi`          | Delete | Points at another distro's shim     |
| `0007` | ubuntu               | `\EFI\ubuntu\shimx64.efi`          | Delete | Distribution wiped                  |
| `2001` | EFI USB Device       | Firmware generated                 | Keep   | Removable media fallback            |
| `2002` | EFI DVD/CDROM        | Firmware generated                 | Keep   | Optical fallback                    |
| `2003` | EFI Network          | Firmware generated                 | Keep   | PXE fallback                        |

The `2001` through `2003` range is generated by the firmware itself, common on Insyde and AMI implementations. Deleting them accomplishes nothing, since they reappear at the next POST.

### Delete and reorder

Delete by explicit slot number, never by pattern:

```bash
for b in 0001 0002 0003 0004 0005 0006 0007; do
  sudo efibootmgr -b "$b" -B
done
```

Then set the order deliberately, rather than trusting whatever the firmware infers:

```bash
sudo efibootmgr -o 0008,0000,2001,2002,2003
sudo efibootmgr -t 3
sudo efibootmgr -v
```

Two follow-ups worth checking. A leftover `BootNext` variable overrides `BootOrder` for exactly one boot and can send you into a deleted entry; clear it with `sudo efibootmgr -N`. And the firmware `Timeout` shown here is entirely separate from `GRUB_TIMEOUT` — a zero here simply means the firmware menu never appears, which is usually what you want when GRUB handles selection.

Some Lenovo and HP firmware re-creates entries for any `\EFI\Boot\bootx64.efi` it finds on the ESP. That behaviour is the reason the next section matters.

## Clean the EFI System Partition

`efibootmgr -B` removes a pointer. The `.efi` binary it referenced is still sitting on the ESP, and firmware that rescans the partition will happily re-register it.

Manjaro mounts the ESP with restrictive permissions, so every listing needs `sudo`:

```bash
sudo ls -la /boot/efi/EFI/
```

Move dead vendor directories aside first and boot once before committing to deletion. This is reversible; `rm -rf` on the wrong path is not:

```bash
sudo mkdir -p /root/esp-quarantine

for d in ubuntu debian deepin refind; do
  sudo mv "/boot/efi/EFI/$d" /root/esp-quarantine/ 2>/dev/null
done
```

Three directories must survive. `Microsoft` holds the Windows loader and its BCD store. `Manjaro` holds your `grubx64.efi`. `Boot` holds `bootx64.efi`, the removable-media fallback path defined by the UEFI specification, which is what rescues you when NVRAM is reset or a firmware update wipes its boot list.

After a successful reboot into both operating systems, delete `/root/esp-quarantine`. The target state:

```bash
sudo ls -1 /boot/efi/EFI/
# Boot
# Manjaro
# Microsoft
```

## Configure GRUB the Native Way

Every setting Grub Customizer was selling you has a supported home in `/etc/default/grub`, and that file is preserved across updates.

```bash
sudo nano /etc/default/grub
```

```bash
GRUB_TIMEOUT=5
GRUB_TIMEOUT_STYLE=menu
GRUB_DEFAULT=saved
GRUB_SAVEDEFAULT=true
GRUB_DISABLE_OS_PROBER=false
```

### The savedefault caveat on Btrfs

`GRUB_SAVEDEFAULT=true` requires `GRUB_DEFAULT=saved` and depends on GRUB writing to `/boot/grub/grubenv` at boot time. GRUB cannot write to a Btrfs or ZFS environment block, so on a default Manjaro Btrfs install the option silently does nothing, and on some builds it prints a warning at boot. If `findmnt -no FSTYPE /boot` returns `btrfs`, set `GRUB_SAVEDEFAULT=false` and pin an explicit default instead:

```bash
GRUB_DEFAULT=0
GRUB_SAVEDEFAULT=false
```

Remember your last OS by muscle memory rather than by an environment block the bootloader cannot write.

### Make Windows detectable

`GRUB_DISABLE_OS_PROBER=false` only helps if the prober exists and can read the Windows partition:

```bash
sudo pacman -S --needed os-prober ntfs-3g
```

Windows Fast Startup leaves the NTFS volume in a hibernated state that Linux refuses to mount read-write, and os-prober then skips it. Disable Fast Startup in Windows under Control Panel, Power Options, Choose what the power buttons do. A full shutdown, not a restart, is required for the setting to take effect.

If Secure Boot is enabled, note that the `shimx64.efi` entries you just deleted were Ubuntu's signed chain. Manjaro's `grubx64.efi` is unsigned by default, so the machine must either run with Secure Boot disabled or use a separately configured shim and machine owner key setup.

### Regenerate and validate

```bash
sudo update-grub
sudo grub-script-check /boot/grub/grub.cfg && echo "Configuration valid"
```

A clean run looks like this:

```text
Generating grub configuration file ...
Found theme: /usr/share/grub/themes/manjaro/theme.txt
Found linux image: /boot/vmlinuz-6.18-x86_64
Found initrd image: /boot/intel-ucode.img /boot/amd-ucode.img /boot/initramfs-6.18-x86_64.img
Warning: os-prober will be executed to detect other bootable partitions.
Found Windows Boot Manager on /dev/nvme0n1p1@/EFI/Microsoft/Boot/bootmgfw.efi
Adding boot menu entry for UEFI Firmware Settings ...
Detecting snapshots ...
Found snapshot: ...
done
```

The `os-prober` warning is informational and expected on modern GRUB releases. The line that matters is `Found Windows Boot Manager`, which confirms the prober reached the ESP.

## Keeping the Repair Durable

The configuration is now owned entirely by Pacman and `/etc/default/grub`, which is exactly what makes it survive kernel updates.

- Reinstalling `grub-customizer` reintroduces the proxy layer. Use `grub-set-default` and `grub-reboot` for one-off boot selection instead.
- After a major `grub` package update, check for `/etc/default/grub.pacnew` and diff it before merging. Pacman will not overwrite your edited file, so new upstream defaults arrive silently in the `.pacnew`.
- Run `sudo pacman -Qkk grub grub-btrfs` after any bootloader package change to confirm no generator script has drifted.
- Firmware updates on some laptops reset `BootOrder` to a Windows-first default. Re-run `sudo efibootmgr -o` afterwards rather than assuming NVRAM is permanent.
- Keep the `Boot` fallback directory on the ESP intact. It is the cheapest insurance you have.

## If the Machine Stops Booting

Boot the Manjaro live ISO in UEFI mode and enter the installed system:

```bash
sudo manjaro-chroot -a
```

From inside the chroot, reinstall the bootloader to the ESP and regenerate the menu:

```bash
grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=Manjaro --recheck
update-grub
```

If the Manjaro NVRAM variable is missing entirely, recreate it against the correct disk and partition number, confirming both with `lsblk -f` first:

```bash
efibootmgr -c -d /dev/nvme0n1 -p 1 -L "Manjaro" -l '\EFI\Manjaro\grubx64.efi'
```

Exit the chroot, reboot, and re-verify `BootCurrent` against `BootOrder`. From that point forward, the menu is generated from packaged scripts and a plain text defaults file, which is a configuration you can actually reason about six months later.

## References

Arch Wiki: GRUB
https://wiki.archlinux.org/title/GRUB

Arch Wiki: Unified Extensible Firmware Interface
https://wiki.archlinux.org/title/Unified_Extensible_Firmware_Interface

efibootmgr(8) manual page
https://man.archlinux.org/man/efibootmgr.8

GNU GRUB Manual
https://www.gnu.org/software/grub/manual/grub/grub.html

grub-btrfs project repository
https://github.com/Antynea/grub-btrfs