---
title: "Installing and Configuring Prism Launcher on Linux Mint"
date: "2026-09-26"
categories: ["Linux", "Gaming"]
tags: ["Minecraft", "Prism Launcher", "Linux Mint", "Flatpak"]
description: "A comprehensive guide to installing, configuring, and optimizing Prism Launcher for Minecraft on Linux Mint."
---
# Installing and Configuring Prism Launcher on Linux Mint

Prism Launcher provides a clean and efficient method for running Minecraft on Linux Mint. It manages distinct game instances, handles Java runtimes cleanly, and makes installing modpacks directly from Modrinth or CurseForge trivial.

## Install Prism Launcher

Linux Mint includes Flatpak and Flathub support by default, making installation straightforward.

1. Open the **Software Manager** from the Mint application menu.
2. Search for `Prism Launcher`.
3. Click **Install**.

Alternatively, install it via the terminal:

```bash
flatpak install flathub org.prismlauncher.PrismLauncher
```

## Initial Setup and Java Runtime

Launch **Prism Launcher** from the applications menu.

1. **Language and Theme:** Select your preferred language and UI styling.
2. **Java Detection:** The Flatpak build typically bundles compatible Java runtimes. If prompted, ensure the following mappings:
   - For **Minecraft 1.20.5 and newer**, use **Java 21**.
   - For **Minecraft 1.17 to 1.20.4**, use **Java 17**.
   - For **Minecraft 1.16.5 and older**, use **Java 8**.

If Prism Launcher reports missing runtimes, install OpenJDK through the terminal:

```bash
sudo apt update
sudo apt install openjdk-21-jre openjdk-17-jre openjdk-8-jre
```

Click **Refresh** inside the Prism Java setup screen and select the matching version.

## Add Your Minecraft Account

1. Click **Accounts** in the top-right of the Prism Launcher window, then select **Manage Accounts**.
2. Click **Add Microsoft**.
3. Prism will display a link to `https://microsoft.com/link` and a short authentication code.
4. Open the link in a web browser, enter the code, and log in with the Microsoft account that owns Minecraft Java Edition.
5. Close the accounts window once verification is complete.

## Create an Instance and Play

1. Click **Add Instance** in the top-left toolbar.
2. Choose your preferred playstyle:
   - **Vanilla:** Select the specific Minecraft version, such as the latest release.
   - **Modded:** Check the box next to your preferred mod loader (Fabric, NeoForge, or Forge). Fabric is recommended for modern versions to achieve optimal performance with mods like Sodium.
   - **Modpacks:** Select **Modrinth** or **CurseForge** from the left panel to browse, search, and install complete modpacks with a single click.
3. Click **OK** to allow Prism Launcher to download the required files.
4. Double-click the instance or click **Launch** in the right-hand panel to start the game.

## Optional Performance Tweaks

- **Allocate More RAM:** Right-click your instance, select **Edit**, navigate to the **Settings** tab, enable **Memory**, and increase the maximum memory allocation. Allocating 4096 MB to 6144 MB is ideal for modded gameplay.
- **GameMode:** If `gamemode` is installed (`sudo apt install gamemode`), enable **GameMode** under the instance wrapper commands to ensure smoother frame delivery.

## References
Prism Launcher Official Website
https://prismlauncher.org/

Flathub Prism Launcher Page
https://flathub.org/apps/org.prismlauncher.PrismLauncher
