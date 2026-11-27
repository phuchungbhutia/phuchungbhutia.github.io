---
title: "Remote Desktop from Android to Manjaro XFCE: Firewall Blocks, Wi-Fi Isolation, and Local VNC Setup"
description: "Troubleshoot firewall blocks, Wi-Fi isolation, and systemd issues when setting up local VNC remote access from Android to Manjaro XFCE."
date: 2026-11-27 12:00:00 +0000
categories: [Linux, Networking, Remote Access]
tags: [manjaro, xfce, x11vnc, fortigate, android, systemd]
---

# Remote Desktop from Android to Manjaro XFCE: Firewall Blocks, Wi-Fi Isolation, and Local VNC Setup

Setting up remote desktop access from an Android phone to a Manjaro Linux workstation often encounters real-world network policy restrictions. Cloud-relayed tools face gateway firewall blocks, while office wireless networks frequently enforce client isolation. This guide documents the exact diagnosis and solutions for these issues, including a clean local VNC setup and complete removal steps.

## Environment Overview

* **Target Desktop**: Manjaro Linux running XFCE on X11 display `:0` (user `lfa`, wireless interface `wlp2s0`).
* **Mobile Client**: Android phone using AVNC or Chrome Remote Desktop.
* **Network Environment**: Managed network protected by FortiGate Application Control with wireless AP/client isolation.

## Problem 1: Chrome Remote Desktop Service Inactive

### Symptom
Checking `systemctl status chrome-remote-desktop@$USER` reports that `chrome-remote-desktop@lfa.service` is `inactive (dead)` and `disabled`.

### Cause
Installing the package and defining `~/.chrome-remote-desktop-session` only prepares the session launcher. The per-user systemd unit does not activate until you authorize the host with a Google setup token and set a PIN.

### Solution
1. Confirm the XFCE session file is in place:
   ```bash
   echo "exec /usr/bin/xfce4-session" > ~/.chrome-remote-desktop-session
   cat ~/.chrome-remote-desktop-session
   ```
2. Visit `https://remotedesktop.google.com/headless` while signed in, click **Begin**, and copy the generated Linux command.
3. Run the command in your Manjaro terminal, enter a host name, and set a 6-digit or longer PIN.
4. Verify the service status:
   ```bash
   systemctl status chrome-remote-desktop@lfa
   ```

## Problem 2: Firefox Timeout on Remote Desktop Setup

### Symptom
Opening the headless setup URL in Firefox fails with `PR_IO_TIMEOUT_ERROR`.

### Cause
The connection timed out before completing. This points to a network, DNS, proxy, or firewall interference on the path to the remote desktop service.

### Solution
1. Test basic connectivity in another browser tab and retry.
2. Disable any active VPN, system proxy, or custom DNS override in Firefox settings.
3. Test reachability from the terminal:
   ```bash
   curl -I --max-time 10 https://remotedesktop.google.com
   ```
4. Flush the local DNS cache if needed:
   ```bash
   sudo resolvectl flush-caches 2>/dev/null || true
   ```

## Problem 3: FortiGate Application Control Blocks Traffic

### Symptom
Accessing the setup page triggers a FortiGate Application Blocked page for `Chrome.Remote.Desktop` under the `Remote.Access` category.

### Cause
The network gateway actively blocks remote-access applications and external relay traffic. Commercial cloud-relayed tools are frequently blocked under these rules.

### Solution
* Respect the network Acceptable Use Policy and check with your administrator for exceptions.
* Pivot to a local VNC server (`x11vnc`) and local VNC client (AVNC) over local TCP port `5900` to bypass external relays.

> Note: Local VNC does not traverse the internet, keeping traffic strictly within your local subnet or direct tethered connection.

## Problem 4: Setting Up x11vnc on Display :0

### Symptom
You need a local VNC server attached to the live XFCE X11 session. The `x11vnc` output prints status messages about `X DAMAGE`, `X COMPOSITE`, or IPv6 `Address already in use`.

### Cause
`x11vnc` reads the active X11 framebuffer directly. Informational notices about X extensions or IPv6 binding failures are normal when IPv4 port `5900` is active and bound.

### Solution
1. Install `x11vnc` and store a VNC password:
   ```bash
   sudo pacman -S x11vnc
   mkdir -p ~/.vnc
   x11vnc -storepasswd ~/.vnc/passwd
   ```
2. Start `x11vnc` bound to display `:0` with persistent multi-client support:
   ```bash
   x11vnc -display :0 -rfbauth ~/.vnc/passwd -forever -shared
   ```
3. Confirm it is listening on IPv4 port `5900` and check the Manjaro Wi-Fi IP:
   ```bash
   ss -tlnp | grep 5900
   ip -4 addr show wlp2s0 | grep inet
   ```

## Problem 5: Packet Loss and AVNC Connection Refused

### Symptom
Pinging the Manjaro IP from the phone results in 100% packet loss. AVNC reports "Connection refused", "Connection timed out", or "Disconnected".

### Cause
Shared or institutional Wi-Fi networks frequently block direct device-to-device traffic via AP/client isolation. Additionally, the host firewall (`ufw` or `firewalld`) may drop incoming TCP port `5900` packets.

### Solution
1. Allow port `5900` on Manjaro local firewall:
   ```bash
   sudo ufw status
   sudo ufw allow from 192.168.0.0/24 to any port 5900 proto tcp
   ```
2. Bypass Wi-Fi client isolation with a direct link:
   * **Android Wi-Fi Hotspot**: Connect Manjaro to the phone hotspot, check the new IP, and connect AVNC to `<hotspot-ip>:5900`.
   * **USB Tethering**: Enable USB tethering on Android, check the active IP via `ip -4 addr show scope global`, and connect AVNC to that IP on port `5900`.
3. Ensure VPN/proxy is off on Android and SSH Tunnel is disabled in AVNC.

## Problem 6: Running x11vnc Automatically in Background

### Symptom
Closing the terminal stops `x11vnc`. You need it to start automatically for your user session without an open terminal window.

### Cause
Foreground commands launched in a terminal are tied to that session unless managed by a systemd service or autostart entry.

### Solution
1. Stop any manually started `x11vnc` process:
   ```bash
   pkill x11vnc
   ```
2. Create `~/.config/systemd/user/x11vnc.service`:
   ```bash
   mkdir -p ~/.config/systemd/user
   cat << 'EOF' > ~/.config/systemd/user/x11vnc.service
   [Unit]
   Description=x11vnc VNC Server for User Session
   After=graphical-session.target

   [Service]
   Type=simple
   ExecStart=/usr/bin/x11vnc -display :0 -rfbauth %h/.vnc/passwd -forever -shared -noxdamage
   Restart=on-failure
   RestartSec=3

   [Install]
   WantedBy=default.target
   EOF
   ```
3. Reload, enable, and start the user service:
   ```bash
   systemctl --user daemon-reload
   systemctl --user enable --now x11vnc.service
   systemctl --user status x11vnc.service
   ```

## Problem 7: Removing All Installed Configurations

### Symptom
You want to clean up all remote desktop services, packages, and configuration files created during setup.

### Cause
Services, packages, and dotfiles remain on disk until explicitly stopped, removed, and deleted.

### Solution
1. Stop and disable services and remove the user systemd unit:
   ```bash
   systemctl --user stop x11vnc.service 2>/dev/null || true
   systemctl --user disable x11vnc.service 2>/dev/null || true
   pkill x11vnc 2>/dev/null || true
   sudo systemctl stop chrome-remote-desktop@lfa 2>/dev/null || true
   sudo systemctl disable chrome-remote-desktop@lfa 2>/dev/null || true
   rm -f ~/.config/systemd/user/x11vnc.service
   systemctl --user daemon-reload
   ```
2. Uninstall the packages and remove configuration directories:
   ```bash
   sudo pacman -Rns x11vnc 2>/dev/null || true
   pamac remove chrome-remote-desktop 2>/dev/null || true
   rm -rf ~/.vnc ~/.chrome-remote-desktop-session ~/.config/chrome-remote-desktop
   ```
3. Uninstall AVNC or Chrome Remote Desktop from your Android device.

## Summary

* Cloud-relayed remote desktop tools frequently fail on managed networks due to FortiGate Application Control and Wi-Fi client isolation.
* Local VNC via `x11vnc` provides a reliable alternative when paired with direct connections like USB tethering or a personal hotspot.
* Managing `x11vnc` via a user-level systemd service ensures persistent background operation without terminal dependency.
* Complete cleanup requires stopping services, removing systemd units, and purging associated configuration directories.

## References

* [Chrome Remote Desktop Headless Setup](https://remotedesktop.google.com/headless)
* [x11vnc GitHub Repository](https://github.com/LibVNC/x11vnc)
* [systemd User Services Documentation](https://wiki.archlinux.org/title/Systemd/User)