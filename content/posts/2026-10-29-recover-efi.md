---
title: "Recovering EFI Partitions and Dual-Boot Setups for Windows and Manjaro"
date: "2026-10-28"
categories: ["Linux", "Windows", "System Administration"]
tags: ["EFI", "GRUB", "Dual-Boot", "Manjaro", "Recovery"]
description: "A comprehensive guide to diagnosing and repairing wiped EFI partitions, restoring Windows BCD stores, and reinstalling GRUB for a functional dual-boot environment."
---

# Recovering EFI Partitions and Dual-Boot Setups for Windows and Manjaro

Dual-booting Windows and Linux provides the flexibility required by many developers and system administrators, but the installation process carries inherent risks. A single misclick in the Calamares installer or an erroneous `mkfs.fat` command can wipe the EFI System Partition (ESP) clean. When this occurs, the machine loses its boot compass: Windows drops into recovery shells with `0xc000000e` errors, and Manjaro fails to load as its GRUB binary and configuration files vanish.

Fortunately, if the underlying NTFS and Linux root partitions remain intact, a full operating system reinstall is unnecessary. By leveraging Hiren’s BootCD PE (HBCD PE) and a Manjaro Live USB, you can reconstruct the EFI structure, restore the Windows Boot Configuration Data (BCD), and reinstall GRUB from scratch.

## Understanding the EFI Architecture

On modern UEFI systems utilizing the GUID Partition Table (GPT), the motherboard firmware bypasses Master Boot Records (MBR) in favor of the EFI System Partition. This small, FAT32-formatted partition (typically 100MB to 512MB) acts as a centralized repository for bootloader binaries.

Inside the ESP, operating systems maintain distinct vendor directories under `/EFI`:
*   **Windows:** Stores files under `/EFI/Microsoft/Boot/`, including `bootmgfw.efi` and the BCD registry hive.
*   **Manjaro:** Stores boot files under `/EFI/manjaro/`, primarily `grubx64.efi`.

When a Linux installer formats the ESP, both directories are deleted. However, the actual operating system files residing on the Windows NTFS partition (`\Windows\System32`) and the Linux root partition (`/`, `/home`) remain untouched. The recovery process focuses solely on rebuilding these pointer files.

## Prerequisites and Tools

To execute this recovery, prepare two USB drives or a single multiboot drive using Ventoy:
1.  **Hiren’s BootCD PE (x64):** A portable Windows 11 PE environment containing native diagnostic and repair utilities.
2.  **Manjaro Live USB:** Official installation media matching your desktop environment (GNOME, KDE Plasma, or XFCE).

Ensure your motherboard UEFI settings are configured correctly before beginning:
*   **Secure Boot:** Disabled (recommended during EFI and GRUB repairs).
*   **Storage Controller Mode:** AHCI or NVMe (avoid Intel RST/RAID unless previously configured).
*   **Boot Mode:** Native UEFI (ensure CSM/Legacy Boot is disabled to prevent installing legacy MBR loaders).

## Phase 1: Restoring Windows via HBCD PE

HBCD PE provides a live Windows environment with full access to deployment tools like `diskpart` and `bcdboot`.

### Inspecting and Mapping Drives

Drive letters in Windows PE are assigned dynamically. You must identify the exact volume letters for the primary Windows partition and the FAT32 EFI partition.

Open an elevated Command Prompt (`Win + R`, type `cmd`, press `Ctrl + Shift + Enter`) and launch `diskpart`:

```powershell
diskpart
list volume
```

Examine the output for two key elements:
*   **Windows OS Volume:** Identified by its size and the presence of the `\Windows` directory (e.g., Volume 1, Letter C).
*   **EFI System Volume:** A FAT32 partition between 100MB and 512MB, often lacking a drive letter (e.g., Volume 2).

Mount the EFI partition to a temporary letter, such as `S:`:

```powershell
select volume 2
assign letter=S
exit
```

If the partition was deleted entirely rather than just formatted, recreate it using `create partition efi` within `diskpart` before assigning the letter.

### Generating the BCD Store

With the EFI partition mounted at `S:` and Windows located at `C:`, use `bcdboot` to copy boot environment files and construct a new BCD store:

```powershell
bcdboot C:\Windows /s S: /f UEFI
```

*   `C:\Windows`: Specifies the source Windows directory.
*   `/s S:`: Specifies the target EFI system partition.
*   `/f UEFI`: Forces generation of UEFI-specific boot files (`bootmgfw.efi`).

Upon success, the terminal will return "Boot files successfully created." At this stage, the machine can boot directly into Windows via the native Windows Boot Manager.

## Phase 2: Restoring Manjaro and Dual-Boot with GRUB

With the Windows EFI directory restored, you can reinstall GRUB. GRUB will register itself in the motherboard's NVRAM, detect the Windows boot files, and generate a unified dual-boot menu.

### Chrooting into the Installed System

Boot into the Manjaro Live USB via UEFI mode. Launch the Terminal and use the automated `manjaro-chroot` tool to discover and mount your installed root filesystem:

```bash
manjaro-chroot -a
```

Select the correct partition if multiple installations are detected. Once inside the chroot environment, verify that the FAT32 EFI partition is mounted at `/boot/efi`:

```bash
lsblk -f
```

If unmounted, mount it manually (replace `/dev/nvme0n1p1` with your actual EFI partition identifier):

```bash
mount /dev/nvme0n1p1 /boot/efi
```

### Reinstalling GRUB and Updating NVRAM

Deploy the GRUB binary into the reconstructed EFI partition:

```bash
grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=manjaro --recheck
```

*   `--target=x86_64-efi`: Compiles the binary for 64-bit UEFI architectures.
*   `--efi-directory=/boot/efi`: Points to the mounted FAT32 partition.
*   `--bootloader-id=manjaro`: Creates the `/EFI/manjaro/` directory and writes `grubx64.efi`.
*   `--recheck`: Clears existing device maps and re-scans storage devices.

### Running os-prober for Windows Auto-Detection

Modern GRUB versions disable `os-prober` by default. Enable it to ensure Windows is detected:

1.  Edit `/etc/default/grub`:
    ```bash
    nano /etc/default/grub
    ```
2.  Locate `GRUB_DISABLE_OS_PROBER=false`. If set to `true` or commented out, change it to `false`.
3.  Save and exit (`Ctrl + O`, `Enter`, `Ctrl + X`).

Generate the configuration file:

```bash
update-grub
```

Look for the line `Found Windows Boot Manager on /boot/efi/EFI/Microsoft/Boot/bootmgfw.efi`. Once confirmed, exit the chroot and reboot:

```bash
exit
reboot
```

## Phase 3: Post-Recovery Validation

After rebooting, verify the following:
*   **GRUB Menu:** Ensure entries for both Manjaro Linux and Windows Boot Manager appear.
*   **Direct Windows Boot:** Test booting Windows from the GRUB menu to confirm the BCD handover functions correctly.
*   **UEFI NVRAM Entries:** If the system boots straight into Windows, enter the BIOS/UEFI settings and move `manjaro` to the top of the boot priority list.

To inspect and modify the boot order from within Linux, use `efibootmgr`:

```bash
sudo efibootmgr -v
sudo efibootmgr -o 0002,0001
```

(Replace `0002` and `0001` with the actual entry numbers for Manjaro and Windows, respectively).

## Best Practices for Future Installations

To prevent future bootloader conflicts:
*   **Verify Partition Actions:** In Calamares manual partitioning, never check the "Format" box for an existing EFI partition unless you intend to wipe all other operating systems. Simply assign the mount point `/boot/efi`.
*   **Allocate Sufficient Space:** Create a 300MB to 512MB EFI partition to provide headroom for multiple kernels and bootloader binaries.
*   **Backup the EFI Directory:** Once stable, back up the contents of the EFI partition:
    ```bash
    sudo tar -czvf ~/efi_backup.tar.gz /boot/efi/EFI
    ```
    This archive allows for rapid restoration of all bootloaders by simply extracting the files into a newly formatted FAT32 partition.

## References

Arch Wiki: GRUB
https://wiki.archlinux.org/title/GRUB

Microsoft Documentation: Bcdboot
https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/bcdboot-command-line-options-techref-di

Manjaro Wiki: Restore GRUB
https://wiki.manjaro.org/index.php?title=Restore_the_GRUB_Bootloader