---
title: "The Ultimate Swiss Army Knife Guide: Setting Up and Mastering MediCat USB"
date: "2026-08-04T10:00:00+05:30"
categories: ["Tech", "Linux"]
tags: ["MediCat USB", "Ventoy", "Windows Repair", "Linux Utilities", "Bootable USB"]
---

# The Complete Swiss Army Knife Guide: Setting Up and Mastering MediCat USB

Whether you are an IT professional, a system administrator, or the designated "tech guy" for family and friends, dealing with unbootable operating systems, malware infections, and locked user accounts is an inevitable headache. Carrying a ring of a dozen different bootable flash drives is a thing of the past.

**MediCat USB** is the ultimate multi-boot diagnostic and repair suite. Built on top of the open-source bootloader **Ventoy**, MediCat turns a single flash drive into a powerful, bootable Swiss Army knife packed with diagnostic environments, password bypass tools, disk partitioners, and malware cleaners.

In this comprehensive guide, we synthesize everything you need to know about setting up MediCat USB, customizing it for smaller drives, navigating its toolset, and using advanced utilities like **Jayro's Lockpick** and **Kon-Boot**.

---

## 1. Understanding the Hardware Requirements

Before downloading files, it's essential to understand MediCat's storage demands:

* **Full MediCat Suite:** Requires at least a **32 GB USB drive** (64 GB recommended). The uncompressed payload sits between **21 GB and 25 GB**.
* **Lightweight Custom Setup:** If you only have a **16 GB USB drive**, you cannot fit the full MediCat package. However, you can use **Ventoy** to create a custom rescue toolkit by manually picking the most critical ISOs.

---

## 2. Setting Up the USB Drive: Step-by-Step

Because MediCat uses **Ventoy** as its underlying core, you don't need to reformat your drive every time you add or update a tool. You simply drag and drop ISO images onto the partition.

### Setup on Windows

1. **Download Tools:** Download `Ventoy2Disk` from [ventoy.net](https://www.ventoy.net) and the official MediCat installer script from [medicatusb.com](https://medicatusb.com/).
2. **Disable Antivirus:** Temporarily disable Windows Security or third-party real-time protection. Password recovery scripts and bootkit utilities inside MediCat naturally trigger security false positives.
3. **Format with Ventoy:** Insert your USB drive, open `Ventoy2Disk.exe`, and select your target drive. Choose **GPT** partition style (recommended for modern UEFI systems) or **MBR** (for legacy BIOS support), then click **Install**.
4. **Run Installer:** Execute `Medicat_Installer.bat` as Administrator. Follow the terminal prompts to select your USB drive letter. The installer will automatically download, extract, and arrange the entire MediCat menu structure onto your drive.

### Setup on Linux

1. **Prepare Ventoy:** Extract `ventoy-x.x.xx-linux.tar.gz`. Open a terminal and run `lsblk` to identify your USB drive (e.g., `/dev/sdb`).
2. **Install Ventoy to Drive:**
```bash
sudo ./Ventoy2Disk.sh -i /dev/sdX

```


*(Replace `/dev/sdX` with your exact USB disk identifier).*
3. **Run MediCat Script:** Run `MediCat_Installer.sh` in the terminal, confirm your target mount path, and let the payload extract directly to the USB drive.

---

## 3. Assembling a Custom Toolkit for a 16 GB Drive

If you are using a 16 GB drive, skip the full MediCat installer script. Instead, format the drive using Ventoy and copy these essential ISOs directly onto the root directory:

| Utility / ISO | Primary Purpose | File Size |
| --- | --- | --- |
| **Mini Windows 10/11 PE** | Complete live desktop environment with diagnostic utilities | ~3.5 GB – 4.5 GB |
| **SystemRescue** | Linux terminal environment for partition and bootloader repair | ~1.2 GB |
| **Kaspersky Rescue Disk** | Bootable offline malware and rootkit scanner | ~670 MB |
| **GParted Live / Clonezilla** | Standalone partition management and disk cloning | ~400 MB – 500 MB |
| **Jayro's Lockpick / Passware** | Windows login, PIN, and account password bypass | ~200 MB – 500 MB |
| **MemTest86** | Deep hardware memory (RAM) stress testing | ~10 MB |

> **Pro Tip:** Keep 2–3 GB of free space on your drive for portable Windows utilities (like CPU-Z, CrystalDiskInfo, or Malwarebytes Portable) that you can launch inside Mini Windows PE.

---

## 4. Deep Dive: What's Included in Full MediCat USB?

When booting the full MediCat USB suite, Ventoy organizes its tools into clean, navigable submenus:

* **Live Operating Systems (~4.5 GB):** Contains *Mini Windows 10/11 PE*, *Active@ Data Studio*, and *SystemRescue*. These allow you to boot into a fully functioning desktop environment even if the computer's primary hard drive is completely dead or corrupted.
* **Backup & Disk Cloning (~3.8 GB):** Features enterprise-grade imaging utilities including *Acronis Cyber Protect Home*, *Macrium Reflect Free*, *AOMEI Backupper*, *Rescuezilla*, and *Clonezilla*.
* **Partition Management & Disk Repair (~2.5 GB):** Includes *AOMEI Partition Assistant*, *EaseUS Partition Master*, *DiskGenius*, and low-level wiping tools like *ShredOS* and *HDAT2*.
* **Password Recovery & Access Controls (~1.2 GB):** Packed with engines like *Jayro's Lockpick*, *Windows Login Unlocker*, *PCUnlocker*, and *NTPWEdit*.
* **Malware & Threat Removal (~4.0 GB):** Features bootable engines for *Malwarebytes*, *Kaspersky*, *Emsisoft*, along with specialized ransomware decryption utilities.
* **Diagnostics & Hardware (~2.0 GB):** Includes *PassMark MemTest86*, *Snappy Driver Installer (SDI)*, *CrystalDiskInfo*, *FurMark*, and *HWMonitor*.

---

## 5. Practical Walkthrough 1: Resetting a Forgotten Windows Password

When a user is permanently locked out of their Windows account, **Jayro's Lockpick** inside MediCat offers a quick, automated way to clear or reset local account credentials.

1. **Boot into MediCat USB:** Enter system BIOS/UEFI during boot.
Insert the MediCat USB drive into the target computer. Turn on the system and tap the boot menu key (**F12**, **F11**, or **Esc**) to select your USB drive from the boot menu.


2. **Launch Jayro's Lockpick or Mini Windows PE:**
In the Ventoy boot menu, go to **Password Recovery** and select **Jayro's Lockpick**. Alternatively, boot into **Mini Windows 10/11 PE**, open the desktop **Portable Apps** launcher, and select `Programs` → `Password Recovery` → `Jayro's Lockpick`.


3. **Select Your Target Windows Installation:**
Launch **Windows Login Unlocker** from the Jayro's Lockpick menu. The utility automatically scans connected hard drives and mounts the local Windows SAM hive directory (`C:\Windows\System32\config\SAM`).


4. **Select the Account and Clear Password:**
Select the locked local user account from the list. Click **Change Password** or **Reset Password**, leave the input field completely blank, and click **OK**.


5. **Apply Changes and Reboot:**
Click **Apply Changes**, close the application, remove the USB drive, and reboot the system. You can now log into Windows by pressing **Enter** without typing a password.


---

## 6. Practical Walkthrough 2: Bypassing Windows Login Without Changing the Password

Resetting a password alters the SAM database, which can disrupt local encryption keys or alert the device owner. If you need to access a system temporarily for maintenance or file recovery without modifying the existing password, **Kon-Boot** is the ideal solution.

### How Kon-Boot Works

Kon-Boot acts as an **in-memory bootkit**. When launched via MediCat, it loads into the computer's volatile RAM and patches the **Local Security Authority Subsystem Service (LSASS)** in memory during boot. It tricks Windows into accepting *any* password (or an empty one) without altering a single byte on the physical hard drive.

1. **Disable Secure Boot in BIOS:** Required because Kon-Boot uses unsigned memory hooks.
Power on the target PC and enter the BIOS settings (**F2**, **Del**, or **F12**). Navigate to the **Security** or **Boot** tab and set **Secure Boot** to **Disabled**. Save and exit.


2. **Boot Kon-Boot from MediCat USB:**
Press your system's boot menu key during restart, boot into MediCat, navigate to **Password Recovery**, and select **Kon-Boot** (`konboot.iso`). Select **Boot in Normal Mode**.


3. **Allow Kon-Boot to Patch RAM:** Do not interrupt the boot sequence.
Watch the Kon-Boot splash screen execute. It will automatically patch system memory and chain-load the internal Windows installation.


4. **Log in with Any Password:**
When the standard Windows login screen appears, select the user account, leave the password field completely **blank** (or type a single character), and press **Enter**.


5. **Restart to Restore Security:**
Perform your diagnostic or backup tasks. When finished, shut down or restart the computer normally and remove the USB drive. On the next boot, Windows will enforce the original, unmodified password once again.


---

## Summary Checklist for Technicians

1. **Drive Choice:** Use a high-speed 32 GB or 64 GB USB 3.0/3.2 flash drive for full MediCat, or a 16 GB drive for custom ISO selection.
2. **Preparation:** Always disable antivirus software on your host machine during drive creation to prevent file quarantine.
3. **BIOS Configurations:** Disable **Secure Boot** when using in-memory tools like Kon-Boot or older diagnostic environments.
4. **BitLocker Caution:** Ensure you have the 48-digit recovery key handy if attempting password bypasses on encrypted systems.
