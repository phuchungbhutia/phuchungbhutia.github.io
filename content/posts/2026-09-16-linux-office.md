---

title: "ONLYOFFICE and LibreOffice Tweaks on Linux Mint XFCE: MS-Office Look, Fonts, and Default Apps"
date: "2026-09-16"
categories: ["Linux", "Desktop Customization"]
tags: ["linux-mint", "xfce", "onlyoffice", "libreoffice", "microsoft-fonts", "default-apps", "howto", "2026"]
description: "Configure ONLYOFFICE, customize LibreOffice to mimic Microsoft Office, install Microsoft core fonts, and set file associations on Linux Mint XFCE."

---

# ONLYOFFICE and LibreOffice Tweaks on Linux Mint XFCE: MS-Office Look, Fonts, and Default Apps

This guide details how to install ONLYOFFICE Desktop Editors, configure LibreOffice to replicate the Microsoft Office user experience, install Microsoft core TrueType fonts, and establish default application handlers for Word, Excel, and PowerPoint file formats on Linux Mint XFCE.

These configuration steps ensure accurate document formatting, table alignments, and layout consistency when exchanging files with Windows-based Microsoft Office environments.

---

## 1. System Package Updates

Update the package lists and upgrade existing packages to establish a clean dependency baseline.

Open a terminal and run:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y

```

---

## 2. Install ONLYOFFICE Desktop Editors

ONLYOFFICE Desktop Editors provides native support for Office Open XML formats (`.docx`, `.xlsx`, `.pptx`), reducing layout shifts and font discrepancies when collaborating with Microsoft Office users.

### Repository Method (Recommended)

Configure the official ONLYOFFICE APT repository and import the verification key:

```bash
# Ensure gnupg directory exists with secure permissions
mkdir -p -m 700 ~/.gnupg

# Import the repository signing key
gpg --no-default-keyring \
    --keyring gnupg-ring:/tmp/onlyoffice.gpg \
    --keyserver hkp://keyserver.ubuntu.com:80 \
    --recv-keys CB2DE8E5

# Set appropriate permissions and install the keyring
chmod 644 /tmp/onlyoffice.gpg
sudo chown root:root /tmp/onlyoffice.gpg
sudo mv /tmp/onlyoffice.gpg /usr/share/keyrings/onlyoffice.gpg

# Add the official repository configuration
echo 'deb [signed-by=/usr/share/keyrings/onlyoffice.gpg] https://download.onlyoffice.com/repo/debian squeeze main' | \
  sudo tee /etc/apt/sources.list.d/onlyoffice.list

# Update repository metadata and install the suite
sudo apt update
sudo apt install -y onlyoffice-desktopeditors

```

Launch ONLYOFFICE from the application menu or execute:

```bash
desktopeditors

```

### Alternative: Direct Package Installation

1. Download the latest Linux `.deb` package (64-bit) from the [official ONLYOFFICE download portal](https://www.onlyoffice.com/download-desktop.aspx).
2. Navigate to your download directory and install the package:

```bash
cd ~/Downloads
sudo apt install ./onlyoffice-desktopeditors_*.deb

```

If dependency errors occur during installation, resolve them with:

```bash
sudo apt --fix-broken install

```

---

## 3. Install Microsoft Core TrueType Fonts

Standard Microsoft fonts (such as Arial, Times New Roman, and Courier New) are essential for rendering documents created on Windows without unexpected line breaks or pagination changes.

Install the installer package:

```bash
sudo apt update
sudo apt install -y ttf-mscorefonts-installer

```

During package configuration, the End User License Agreement (EULA) prompt will display:

1. Press `Tab` to select **`<Ok>`**, then press `Enter`.
2. Select **`<Yes>`** to accept the license terms, then press `Enter`.

Update the font information cache:

```bash
sudo fc-cache -f -v

```

Verify that the fonts are correctly registered:

```bash
fc-list | grep -iE "arial|times new roman|courier new"

```

---

## 4. Customize LibreOffice to Resemble Microsoft Office

LibreOffice includes alternative interface layouts and icon sets that align closely with modern versions of Microsoft Office.

### 4.1 Enable the Tabbed Ribbon Interface

1. Open LibreOffice Writer, Calc, or Impress.
2. Navigate to **View → User Interface**.
3. Select **Tabbed** (or **Tabbed Compact** for displays with limited vertical resolution).
4. Choose **Apply to all** to standardize the layout across Writer, Calc, and Impress.
5. Click **Close**.

### 4.2 Set the Icon Style to Colibre

1. Navigate to **Tools → Options**.
2. Under **LibreOffice → View**, locate the **Icon Style** setting.
3. Select **Colibre** (or **Colibre (Dark)** when running a dark system theme).
4. Optionally adjust **Icon Size** to **Automatic** or **Small**.
5. Click **Apply**, then **OK**.

### 4.3 Configure Default File Formats

Configure LibreOffice to save new documents in Microsoft Office formats by default:

1. Navigate to **Tools → Options → Load/Save → General**.
2. Under the **Default File Format and ODF Settings** section, set **Always save as**:
* **Text document:** `Microsoft Word 2007–365 (*.docx)`
* **Spreadsheet:** `Microsoft Excel 2007–365 (*.xlsx)`
* **Presentation:** `Microsoft PowerPoint 2007–365 (*.pptx)`


3. Click **Apply**, then **OK**.

### 4.4 Adjust Toolbars and Sidebars

* Right-click any active toolbar segment and select **Customize Toolbar...** to add or remove individual tool controls.
* Toggle the contextual tool panel via **View → Sidebar** (or press `Ctrl + F13` / `Ctrl + F5` depending on keymap settings).

---

## 5. Set Default Applications for Office Formats

Configure file associations to ensure that `.docx`, `.xlsx`, and `.pptx` documents launch in your preferred office suite automatically.

### System Settings Method

1. Open the application menu, search for **Preferred Applications**, and press `Enter`.
2. Locate the **Utilities** or file management category.
3. Select your preferred application for text documents, spreadsheets, and presentations.
4. Close the window to save the preferences.

### File Manager Method (Thunar)

To configure associations per file extension:

1. Open **Thunar File Manager**.
2. Right-click any `.docx` file and select **Properties**.
3. Switch to the **Open With** tab.
4. Highlight **ONLYOFFICE Desktop Editors** (or **LibreOffice Writer**).
5. Click **Set as Default**.
6. Repeat this process for an `.xlsx` file and a `.pptx` file.

### Configuration File Method (`mimeapps.list`)

You can also define these associations directly in your user MIME profile:

```bash
nano ~/.config/mimeapps.list

```

Add or modify the following entries under the `[Default Applications]` section:

#### For ONLYOFFICE

```ini
[Default Applications]
application/vnd.openxmlformats-officedocument.wordprocessingml.document=onlyoffice-desktopeditors.desktop
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet=onlyoffice-desktopeditors.desktop
application/vnd.openxmlformats-officedocument.presentationml.presentation=onlyoffice-desktopeditors.desktop
application/msword=onlyoffice-desktopeditors.desktop
application/vnd.ms-excel=onlyoffice-desktopeditors.desktop
application/vnd.ms-powerpoint=onlyoffice-desktopeditors.desktop

```

#### For LibreOffice

```ini
[Default Applications]
application/vnd.openxmlformats-officedocument.wordprocessingml.document=libreoffice-writer.desktop
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet=libreoffice-calc.desktop
application/vnd.openxmlformats-officedocument.presentationml.presentation=libreoffice-impress.desktop
application/msword=libreoffice-writer.desktop
application/vnd.ms-excel=libreoffice-calc.desktop
application/vnd.ms-powerpoint=libreoffice-impress.desktop

```

Save the file (`Ctrl + O`, then `Enter`) and exit (`Ctrl + X`). Restart Thunar to apply the changes immediately:

```bash
thunar -q && thunar &

```

---

## 6. Automated Setup Script

Save the following script as `setup-office-mint.sh` to automate repository configuration, font installation, and package deployment:

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "=== Updating package index ==="
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y

echo "=== Installing Microsoft core fonts ==="
sudo apt install -y ttf-mscorefonts-installer
sudo fc-cache -f -v

echo "=== Configuring ONLYOFFICE repository ==="
mkdir -p -m 700 ~/.gnupg
gpg --no-default-keyring \
    --keyring gnupg-ring:/tmp/onlyoffice.gpg \
    --keyserver hkp://keyserver.ubuntu.com:80 \
    --recv-keys CB2DE8E5 || true
chmod 644 /tmp/onlyoffice.gpg
sudo chown root:root /tmp/onlyoffice.gpg
sudo mv /tmp/onlyoffice.gpg /usr/share/keyrings/onlyoffice.gpg

echo 'deb [signed-by=/usr/share/keyrings/onlyoffice.gpg] https://download.onlyoffice.com/repo/debian squeeze main' | \
  sudo tee /etc/apt/sources.list.d/onlyoffice.list

echo "=== Installing ONLYOFFICE Desktop Editors ==="
sudo apt update
sudo apt install -y onlyoffice-desktopeditors

echo "=== Setup complete ==="

```

Make the script executable and run it:

```bash
chmod +x setup-office-mint.sh
./setup-office-mint.sh

```

---

## 7. Troubleshooting

### ONLYOFFICE Missing from "Open With" Context Menus

Verify that the application desktop entry exists in the system directory:

```bash
ls /usr/share/applications | grep -i onlyoffice

```

If the desktop entry is missing, reinstall the package:

```bash
sudo apt install --reinstall onlyoffice-desktopeditors

```

Update the local desktop application database:

```bash
update-desktop-database ~/.local/share/applications 2>/dev/null || true

```

### LibreOffice Interface Modifications Do Not Persist

1. Close all active LibreOffice windows, including quick-launch background processes.
2. Relaunch Writer and confirm settings under **View → User Interface** and **Tools → Options → View**.
3. If adjustments fail to save, confirm write permissions on the user configuration directory:

```bash
ls -ld ~/.config/libreoffice

```

### Font Substitution Issues in Rendered Documents

Verify that the TrueType font files are active:

```bash
fc-list : family | grep -i "arial"

```

Open LibreOffice and navigate to **Tools → Options → LibreOffice → Fonts**. Verify that the **Replacement table** is not actively substituting core Microsoft fonts with alternate system fonts.

---

## References

1. [ONLYOFFICE Desktop Editors Installation Guide](https://www.onlyoffice.com/download-desktop.aspx)
2. [How to Make LibreOffice Look and Work Like Microsoft Office](https://dtptips.com/how-to-make-libreoffice-look-and-work-like-microsoft-office-2025-detailed-guide/)
3. [LibreOffice Interface Customization Documentation](https://libreoffice.pl/en/libreoffice-from-scratch-part-1-configuration-and-interface-customization-2/)
4. [Installing Microsoft Core Fonts on Debian-Based Distributions](https://linuxcapable.com/how-to-install-microsoft-fonts-on-debian-linux/)
5. [Using Office File API and TrueType Fonts on Linux](https://docs.devexpress.com/OfficeFileAPI/401441/installation-guide/use-office-file-api-on-linux)
6. [Managing Default Applications and MIME Profiles in Linux Mint](https://coin.frontpagelinux.com/16429905/how-do-i-set-default-applications/)
