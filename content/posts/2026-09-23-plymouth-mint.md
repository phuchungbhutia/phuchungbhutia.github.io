---
title: "Customizing Linux Mint: How to Change the Plymouth Boot Splash Animation"
date: "2026-09-23"
categories: ["Linux", "Desktop Customization"]
tags: ["linux-mint", "plymouth", "boot-animation", "grub", "terminal", "2026"]
description: "A complete step-by-step technical guide to changing, previewing, and troubleshooting Plymouth boot splash animations in Linux Mint."
---

# Customizing Linux Mint: How to Change the Plymouth Boot Splash Animation

Linux Mint relies on Plymouth during startup to mask raw kernel initialization logs with an aesthetic, animated splash screen. While the default Mint logo provides a clean and familiar boot transition, Plymouth is modular, allowing users to swap out default themes, install community-built animations, or design custom splash screens. Modifying this system involves querying available themes, configuring the system alternatives manager, and regenerating the initial RAM file system (initramfs) so that the new assets load into memory before your root drive mounts.

## Understanding the Plymouth Architecture

During the early stages of boot, the Linux kernel initializes low-level hardware drivers before mounting your primary root filesystem. Plymouth runs inside the initramfs (initial RAM filesystem), drawing directly to your framebuffer using Direct Rendering Manager (DRM) or Kernel Mode Setting (KMS).

Plymouth themes reside within the system graphics tree:

- System Themes Directory: `/usr/share/plymouth/themes/`
- Default Theme Link: `/etc/alternatives/default.plymouth`
- Core Binary and Engine: `/usr/sbin/plymouthd` and `/usr/bin/plymouth`

Because themes run from the initramfs rather than live disk storage, whenever you select a new theme, you must update the initramfs image. Skipping this step causes the system to keep displaying the old theme cached inside the existing image.

## Listing and Installing New Themes

Linux Mint comes with minimal pre-installed Plymouth themes. You can verify what is currently available on your machine or fetch pre-packaged packages directly from the official repositories.

### Step 1: Check Current and Available Themes

List the Plymouth themes currently present on your machine:

```bash
plymouth-set-default-theme --list
```

To see which theme is actively selected:

```bash
plymouth-set-default-theme
```

### Step 2: Install Additional Repository Themes

The default repositories provide various legacy Ubuntu and Debian splash animations:

```bash
sudo apt update
sudo apt install plymouth-themes
```

This package installs additional animations including breeze, fade-in, glow, script, and solar. Verify the updated catalog:

```bash
plymouth-set-default-theme --list
```

## Changing the Active Boot Theme

Switching your active boot animation can be completed using either the `plymouth-set-default-theme` tool or the Debian system alternatives manager (`update-alternatives`).

### Method A: Using plymouth-set-default-theme

This utility sets the default theme and can update the initial ramdisk in a single step using the `-R` flag.

Select your preferred theme (for example, solar) and rebuild the image:

```bash
sudo plymouth-set-default-theme -R solar
```

If you prefer to rebuild initramfs manually to inspect the build output:

```bash
sudo plymouth-set-default-theme solar
sudo update-initramfs -u
```

### Method B: Using update-alternatives

If you prefer an interactive menu that lists all registered themes, use `update-alternatives`:

- Launch the interactive selector:

```bash
sudo update-alternatives --config default.plymouth
```

- The terminal displays a numbered table of registered themes:

```text
There are 5 choices for the alternative default.plymouth (providing /usr/share/plymouth/themes/default.plymouth).

  Selection    Path                                                            Priority   Status
------------------------------------------------------------
* 0            /usr/share/plymouth/themes/mint-logo/mint-logo.plymouth          150       auto mode
  1            /usr/share/plymouth/themes/breeze/breeze.plymouth                100       manual mode
  2            /usr/share/plymouth/themes/mint-logo/mint-logo.plymouth          150       manual mode
  3            /usr/share/plymouth/themes/solar/solar.plymouth                  50        manual mode
  4            /usr/share/plymouth/themes/spinfinity/spinfinity.plymouth        50        manual mode

Press <enter> to keep the current choice[*], or type selection number:
```

- Type the number corresponding to your chosen theme and press Enter.
- Rebuild the initramfs to write the new selection into memory:

```bash
sudo update-initramfs -u
```

## Installing Third-Party or Custom Plymouth Themes

You can install community-created themes distributed via platforms like GNOME-Look or GitHub.

### Step 1: Place Theme Files in the Themes Directory

Community themes usually unpack as a folder containing image sequences and a `.plymouth` configuration file. Extract your downloaded theme directly to the system directory:

```bash
sudo cp -r ~/Downloads/cyberpunk-theme /usr/share/plymouth/themes/
```

Confirm that the folder structure contains the `.plymouth` definition file:

```bash
ls -l /usr/share/plymouth/themes/cyberpunk-theme/
```

### Step 2: Register the Theme with update-alternatives

Before Plymouth recognizes a custom folder, register it in the system alternatives database:

```bash
sudo update-alternatives --install /usr/share/plymouth/themes/default.plymouth default.plymouth /usr/share/plymouth/themes/cyberpunk-theme/cyberpunk-theme.plymouth 100
```

### Step 3: Set and Apply the Custom Theme

```bash
sudo plymouth-set-default-theme -R cyberpunk-theme
```

## Previewing Your Boot Animation Without Rebooting

Rebooting repeatedly to test animations is inefficient. You can test your splash animation directly from a running desktop session using Plymouth daemon controls.

Open a terminal and run the following sequence to launch an in-window preview:

```bash
sudo plymouthd --debug --mode=boot
sudo plymouth show-splash
```

Observe the rendered graphics. Once finished reviewing, close the preview cleanly:

```bash
sudo plymouth quit
```

> **Note:** If the preview does not display inside an active X11 or Wayland desktop session, switch to a virtual console (Ctrl + Alt + F3), run the commands, and switch back to your desktop (Ctrl + Alt + F7 or Ctrl + Alt + F2).

## Configuring GRUB Resolution for Sharp Animations

If your splash animation appears stretched, blurry, or drops directly to text mode during boot, GRUB may be initializing at a fallback resolution (such as 640x480). Setting the bootloader to match your panel native display resolution fixes this.

- Open `/etc/default/grub` in an editor:

```bash
sudo xed /etc/default/grub
```

- Ensure the kernel command-line variables include `quiet` and `splash`:

```text
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
```

- Locate `GRUB_GFXMODE`. Remove any leading `#` comment symbol and set it to your monitor native dimensions:

```text
GRUB_GFXMODE=1920x1080
```

- Instruct GRUB to keep that resolution handed off cleanly to the kernel payload by adding this line immediately below `GRUB_GFXMODE`:

```text
GRUB_GFXPAYLOAD_LINUX=keep
```

- Save the file and refresh your bootloader configuration:

```bash
sudo update-grub
```

## Troubleshooting Plymouth Boot Issues

| Symptom | Probable Cause | Corrective Action |
|---|---|---|
| Old theme remains visible after reboot | `update-initramfs` was omitted | Run `sudo update-initramfs -u` to rebuild the boot image. |
| Black screen with text scrolling instead of splash | Missing `splash` kernel parameter | Check `/etc/default/grub` for `quiet splash` and run `sudo update-grub`. |
| Animation looks stretched or pixelated | Framebuffer set to 640x480 or 800x600 | Define `GRUB_GFXMODE=1920x1080` in `/etc/default/grub`. |
| Custom theme does not appear in theme lists | Missing or misnamed `.plymouth` file | Ensure the file inside `/usr/share/plymouth/themes/<name>/` matches `<name>.plymouth`. |

- **Restoring the Stock Mint Theme:** If a custom theme fails to load, reset Plymouth back to default:

```bash
sudo plymouth-set-default-theme -R mint-logo
```

- **Inspecting Early Boot Logs:** If boot animations fail completely, inspect previous boot messages for Plymouth initialization errors:

```bash
journalctl -b -0 -u plymouth*
```

## References

Plymouth Project Documentation
https://www.freedesktop.org/wiki/Software/Plymouth/

Linux Mint Community Forums
https://forums.linuxmint.com/
