---
title: "The Ultimate Guide to Windows Password Recovery: Bootable Rescue Disks, SAM Editing, and the Utilman Exploit"
date: "2026-09-15 20:20:00 +0530"
categories: ["Windows", "Sysadmin"]
tags: ["windows-11", "windows-10", "hirens-bootcd", "chntpw", "lazesoft", "utilman", "password-reset", "sysadmin", "2026"]
description: "A complete technical guide to breaking out of Windows lock screens using Hiren's BootCD PE, Lazesoft, chntpw SAM manipulation, and the native offline Utilman replacement workaround."

---

Getting locked out of a Windows workstation is a classic IT support nightmare. Whether an endpoint lost its domain connection, a user forgot their offline password, or an inherited PC arrived without credentials, reinstalling the entire operating system from scratch is rarely an acceptable first choice.

Underneath the modern Windows Hello PINs and lock screen aesthetics lies the legacy Windows NT authentication architecture: the Security Accounts Manager (SAM) database. 

With the right bootable rescue environment or a quick trip into Windows Recovery, you can clear passwords, manipulate user flags, or spawn an elevated shell to regain administrative access in minutes.

---

### Critical Ground Rules Before You Begin

Before burning an ISO or altering system binaries, determine two factors about the target machine:

1. **Local Account vs. Microsoft Account:**
   Offline rescue tools edit the local Windows SAM hive on disk. They can instantly clear passwords on **local accounts**. However, if the machine signs in via an online **Microsoft Account** (`user@outlook.com`), these tools cannot change credentials stored on Microsoft's cloud servers. Instead, they can convert the cloud account to a local profile or unlock the built-in, disabled Administrator account.
2. **BitLocker Encryption:**
   If BitLocker or Device Encryption is active, the drive's file system is encrypted at rest. Offline boot environments cannot read or alter the SAM hive or system binaries unless you provide the **48-digit BitLocker Recovery Key** during boot. Attempting to force-modify an encrypted volume without the key risks permanent data loss.

---

### Method 1: Hiren’s BootCD PE (GUI-Driven & Intuitive)

**Hiren’s BootCD PE** is based on Windows 11 PE (Preinstallation Environment). It boots into a familiar desktop interface with full driver support and storage recognition.


```

[Target PC] ──► Boot via USB ──► Windows PE Desktop ──► Windows Login Unlocker ──► Clear Password

```

#### Provisioning the Media
1. Download the official ISO from the Hiren’s BootCD PE portal on a secondary machine.
2. Flash the ISO to an empty USB flash drive (at least 4GB) using **Rufus**:
   * **Partition scheme:** `GPT` (for modern UEFI systems) or `MBR` (for legacy BIOS).
   * **Target system:** `UEFI (non-CSM)`.

#### Execution Procedure
1. Insert the USB drive into the locked machine and boot into the firmware boot selection menu (tap `F12` on Dell/Lenovo, `F9` on HP, or `Esc`/`F8` on ASUS/others).
2. Boot into the Windows PE desktop environment.
3. Open the Start menu and navigate to:

```

All Programs > Security > Passwords > Windows Login Unlocker

```
4. The utility will automatically scan all mounted volumes, parse the offline SAM database, and list local accounts.
5. Right-click the locked username and select **Reset Password** (or **Clear Password**).
6. Confirm the prompt, close the utility, unmount the USB drive, and reboot. The local account will sign in without prompting for credentials.

---

### Method 2: Lazesoft Recover My Password (Wizard-Guided)

For users who prefer a step-by-step assistant without navigating through menus, **Lazesoft Recover My Password Home Edition** automates media creation and SAM unlocking through a clean wizard.

#### Execution Procedure
1. Install and run Lazesoft on a functioning PC.
2. Click **Burn CD/USB Disk** and follow the automated prompts to configure a bootable flash drive.
3. Boot the locked computer from the Lazesoft USB drive.
4. Select **Lazesoft Live CD** from the boot loader.
5. Choose **Password Recovery**, confirm the detected Windows installation path, and choose **Reset Local Password**.
6. Highlight the target user account, click **Next**, and choose **Reset/Blank Password**.
7. Restart the system.

---

### Method 3: `chntpw` / Offline NT Password Editor (Linux SAM Manipulation)

If you prefer lightweight Linux-based environments or already have a live Linux USB (such as Ubuntu, Arch, or Fedora), **`chntpw`** (Change NT Password) is a battle-tested command-line utility that writes changes directly to the raw SAM hive.

#### Installing `chntpw` on Live Linux
If you booted into a live Ubuntu desktop rather than a dedicated rescue CD, open a terminal and pull the package:

```bash
sudo apt update && sudo apt install -y chntpw

```

#### Direct SAM File Manipulation

Mount the Windows partition and access the registry configuration directory:

```bash
# Locate your Windows NTFS partition (e.g., /dev/nvme0n1p3 or /dev/sda3)
lsblk

# Mount the target drive
sudo mkdir -p /mnt/windows
sudo mount /dev/nvme0n1p3 /mnt/windows

# Navigate to the Windows registry config directory
cd /mnt/windows/Windows/System32/config/

```

Launch `chntpw` against the SAM database:

```bash
sudo chntpw -i SAM

```

This launches an interactive menu inside the terminal:

```
======== chntpw Interactive Menu ========
 1 - Edit user data and passwords
 2 - List users
 q - Quit

```

1. Enter `1` to **Edit user data and passwords**.
2. Type the exact username or the RID (e.g., `01f4` for the built-in Administrator) and press **Enter**.
3. Select an action:
* Enter `1` to **Clear (blank) user password**.
* Enter `2` to **Unlock and enable user account** (useful if an account is locked out or disabled).


4. Enter `q` to quit the user editor.
5. Enter `q` to exit the main menu.
6. **Crucial Verification Step:** When prompted:

```
About to write file(s) back! Do it? [y/n] :

```


Press `y` and hit **Enter** to write the modifications back to the disk.

Unmount the volume and reboot:

```bash
cd ~
sudo umount /mnt/windows
sudo reboot

```

---

### Method 4: The Built-in "Utilman" Replacement (Zero External Tools Required)

If you are stranded without a secondary PC or a USB drive, you can execute an offline binary swap directly through the native **Windows Recovery Environment (WinRE)**.

#### The Concept

Before anyone logs into Windows, the operating system runs lock screen helpers—including the Ease of Access utility (`utilman.exe`)—under the privileged `NT AUTHORITY\SYSTEM` account. By temporarily replacing `utilman.exe` with `cmd.exe`, clicking the accessibility icon opens an interactive command prompt directly at the lock screen.

```
[Lock Screen] ──► Click Accessibility Icon ──► Launches utilman.exe ──► Actually runs cmd.exe (SYSTEM Privileges)

```

#### Step 1: Boot into Windows Recovery Environment

1. At the Windows login screen, hold down the physical **Shift key** on your keyboard while clicking **Power > Restart**.
2. Once the blue recovery menu appears, navigate to:

```
Troubleshoot > Advanced options > Command Prompt

```



#### Step 2: Swap the Binaries via Command Line

In WinRE, drive letters frequently shift. The Windows system partition is usually reassigned to `D:` or `E:`, while `X:` represents the temporary recovery RAM disk.

Locate your real Windows drive:

```cmd
:: Check drive letters until you find the Windows directory
dir D:\Windows
dir E:\Windows

```

Once confirmed (assuming `D:` holds your installation), run:

```cmd
:: 1. Back up the original Accessibility utility
move D:\windows\system32\utilman.exe D:\windows\system32\utilman.bak

:: 2. Copy the command prompt shell in its place
copy D:\windows\system32\cmd.exe D:\windows\system32\utilman.exe

:: 3. Reboot the machine
wpeutil reboot

```

#### Step 3: Trigger CMD and Set Credentials

1. When the normal Windows 11 lock screen loads, click the **Accessibility icon** (the person or gauge icon in the bottom-right corner).
2. A Command Prompt window will pop up with full `SYSTEM` authority.
3. Reset your existing local user password:

```cmd
net user <Username> <NewPassword>

```


*To make the password completely blank, run:*

```cmd
net user <Username> *

```
*(Hit Enter twice).*

4. If you were locked out of an online Microsoft Account, create a brand-new local administrator account instead:

```cmd
net user RecoveryAdmin Pass#2026! /add
net localgroup administrators RecoveryAdmin /add

```


5. Close the terminal and sign in with the new credentials.

#### Step 4: Security Cleanup (Reversing the Swap)

Never leave an elevated command prompt attached to your lock screen. Once logged in, open an administrative terminal or boot back into WinRE to restore the original binary:

```cmd
del D:\windows\system32\utilman.exe
move D:\windows\system32\utilman.bak D:\windows\system32\utilman.exe

```

---

### Quick Comparison of Recovery Approaches

| Method | UI Type | Complexity | Best For | Offline Media Required? |
| --- | --- | --- | --- | --- |
| **Hiren’s BootCD PE** | Full Windows PE GUI | Low | Beginners, full storage driver support | Yes (USB) |
| **Lazesoft Recovery** | Guided Wizard | Lowest | Non-technical home users | Yes (USB) |
| **`chntpw`** | CLI / Interactive TUI | Moderate | Linux users, dual-boot setups, fast headless resets | Yes (USB) |
| **Utilman Exploit** | Command Prompt | Moderate | Emergency situations with no extra hardware | **No** (Uses WinRE) |

With these recovery vectors at your disposal, a forgotten password or broken login token can be resolved systematically without reinstalling the operating system or losing local user files.
