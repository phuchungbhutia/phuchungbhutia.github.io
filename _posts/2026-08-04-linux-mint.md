---
title: "Linux Mint Power-User Manual: HP Printers, Dependencies, Fonts, and Package Management"
date: "2026-08-04"
categories: ["Linux", "System Administration", "Open Source"]
tags: ["linux-mint", "hplip", "cups", "apt", "dpkg", "libreoffice", "fonts"]
---

Migrating to Linux Mint provides a fast, privacy-respecting, and highly customizable desktop environment. However, transitioning away from proprietary operating systems often introduces a learning curve—particularly when managing hardware drivers, fixing print services, dealing with document layout changes, and navigating package dependency issues.

This comprehensive reference guide aggregates essential Linux Mint administration workflows, command-line solutions, and troubleshooting techniques into a single, structured manual.

---

## 1. Managing HP Hardware via HPLIP and CUPS

Linux Mint uses the **Common Unix Printing System (CUPS)** to handle print queues and job spools, alongside **HPLIP (HP Linux Imaging and Printing)** for HP device communication, driver support, and status monitoring.

### Installing the HPLIP Stack

While Linux Mint ships with base printing tools, installing the full HPLIP suite ensures access to status utilities, scanner support, and device wizards.

```bash
sudo apt update
sudo apt install hplip hplip-gui

```

To run the interactive hardware discovery wizard for USB, Network, or Wi-Fi printers:

```bash
hp-setup

```

*Note: Models requiring proprietary binary drivers (such as many HP LaserJet printers) will prompt you to download and install the required plugin directly through the `hp-setup` wizard.*

### Print Service Management

When print jobs hang or the queue fails to process documents, restarting the underlying daemon fixes the issue in most cases:

* **Restart CUPS:** `sudo systemctl restart cups`
* **Stop CUPS:** `sudo systemctl stop cups`
* **Start CUPS:** `sudo systemctl start cups`
* **Check Service Status:** `sudo systemctl status cups`

To manage the graphical taskbar applet:

```bash
hp-systray     # Launches the desktop tray monitor
hp-systray -x  # Terminates the tray applet process

```

### Resolving "Device Communication Error"

If your system loses communication with your printer, work through these diagnostic procedures sequentially:

1. **Reinstall Proprietary Plugins:** Force an update of the binary plugin stack.
```bash
hp-plugin -i

```


2. **Execute Diagnostic Checks:** Run the built-in diagnostic utility to identify missing packages or configuration errors:
```bash
hp-check -t

```


3. **Verify User Permissions:** Ensure your current Linux account belongs to the appropriate hardware control groups:
```bash
sudo usermod -a -G lp,scanner $USER

```


*(Log out and log back in for changes to take effect).*
4. **Purge a Stuck Print Queue:** Clear corrupted spool files directly from the spool directory:
```bash
sudo systemctl stop cups
sudo rm /var/spool/cups/*
sudo systemctl start cups

```



---

## 2. Advanced Document Workflow: Booklet Printing

Most Linux desktop applications lack a one-click "Booklet/Brochure" option in standard print dialogs. You can accomplish proper page ordering using any of the following methods.

### Method A: Boomaga Virtual Printer (Recommended)

Boomaga acts as an intermediate print preview utility that automatically reorders pages into proper signature formats prior to sending the job to physical hardware.

```bash
sudo apt install boomaga

```

* **Workflow:** Open your document $\rightarrow$ Print to **Boomaga** $\rightarrow$ Select **Booklet Mode** $\rightarrow$ Send to your physical HP printer.

### Method B: LibreOffice Native Layout

1. Navigate to **File > Print**.
2. Select the **Page Layout** tab.
3. Under the layout options, choose **Brochure**.
4. In your printer's duplex settings, set orientation to **Two-Sided (Short-Edge Flip)**.

### Method C: Command-Line Processing (`pdfbook2`)

To convert an existing PDF into a booklet format via the terminal:

```bash
sudo apt install texlive-extra-utils
pdfbook2 --paper=letter input_document.pdf

```

This command outputs a file named `input_document-book.pdf`, pre-formatted for 2-up double-sided printing.

---

## 3. Microsoft Font Integration and Compatibility

Document rendering issues in LibreOffice or OnlyOffice often occur because proprietary Microsoft fonts are missing, causing text to wrap incorrectly across pages.

### Installing Core Microsoft Fonts

To install standard web fonts (Arial, Times New Roman, Courier New):

```bash
sudo apt update && sudo apt install ttf-mscorefonts-installer

```

> **Terminal Navigation Note:** When the text-based EULA agreement appears during installation, press the **Tab** key to select **`<Ok>`**, press **Enter**, select **`Yes`**, and press **Enter** again.

### Installing Modern Proprietary Fonts (Calibri, Cambria, Segoe UI)

For newer Microsoft font families, manually copy the `.ttf` files from a Windows installation or backup directory:

1. Create the user font directory:
```bash
mkdir -p ~/.fonts

```


2. Place your `.ttf` or `.otf` files inside `~/.fonts/`.
3. Refresh the local system font cache:
```bash
sudo fc-cache -fv

```



### Metric Equivalents

If you prefer to stick to fully open-source fonts, Linux Mint includes metrically compatible alternatives that maintain document spacing without layout distortion:

| Microsoft Font | Open-Source Equivalent |
| --- | --- |
| **Arial** | Liberation Sans / Arimo |
| **Times New Roman** | Liberation Serif / Tinos |
| **Courier New** | Liberation Mono / Cousine |
| **Calibri** | Carlito |
| **Cambria** | Caladea |

---

## 4. Package Management and Troubleshooting

Linux Mint uses Debian Package files (`.deb`) and the Advanced Package Tool (`apt`) for software management.

### Resolving GPG Repository Signature Errors (`NO_PUBKEY`)

When third-party software repositories update their security keys, `sudo apt update` may fail with an unverified key error (e.g., `NO_PUBKEY FD533C07C264648F`).

To resolve this issue, import the missing public key directly from an official keyserver:

```bash
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys FD533C07C264648F
sudo apt update

```

Alternatively, fetch and dearmor the key directly into your trusted keyrings directory:

```bash
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg
sudo apt update

```

### Installing Standalone `.deb` Files

Avoid using `dpkg -i` to install standalone package files directly. `dpkg` is a low-level tool that cannot resolve or fetch missing remote dependencies.

```bash
# INCORRECT: Leaves missing dependencies unconfigured
sudo dpkg -i package_name.deb

```

**The Preferred Installation Method:**
Use `apt` to install local `.deb` files so it automatically fetches any required dependency packages from online repositories:

```bash
sudo apt install ./package_name.deb

```

*(The leading `./` is required to notify `apt` that you are referencing a local filesystem path).*

### Recovering from Broken Dependency States

If a package installation halts due to unmet dependency requirements, your system's package database enters an unconfigured state. Fix the broken installations by running:

```bash
sudo apt install -f

```

The `-f` (`--fix-broken`) flag instructs `apt` to inspect unresolved dependencies, download the required missing libraries, and finish configuring all pending software installations.
