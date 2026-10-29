---
title: "Troubleshooting the Intel Wi-Fi 6 AX101 on Linux Mint: A Deep-Dive Postmortem"
date: "2026-10-28"
categories: ["Linux", "Hardware", "Networking"]
tags: ["Intel AX101", "iwlwifi", "CNVi", "Linux Mint", "Troubleshooting"]
description: "A technical guide to resolving signal dropouts, firmware panics, and connection failures for Intel CNVi Wi-Fi adapters on Linux Mint."
---

# Troubleshooting the Intel Wi-Fi 6 AX101 on Linux Mint: A Deep-Dive Postmortem

Few Linux issues are as baffling as watching your desktop tray show a crisp, full 100% Wi-Fi signal right next to your home router, only to see the connection endlessly state "connecting...", drop into "Activation of network connection failed," or abruptly shut the entire wireless interface off.

This scenario was recently resolved on an Acer Aspire Lite (AL15G-52) running Linux Mint Cinnamon, powered by the Intel Alder Lake-P CNVi AX101 (Harrison Peak) module. The following is a complete technical breakdown of why this happens, how to decode low-level kernel driver errors, and the end-to-end fixes that permanently stabilize the connection.

## Part 1: The Anatomy of a "Ghost" Connection

When a Wi-Fi card shows full signal strength but refuses to connect, users often blame their ISP or router. However, in the Linux wireless networking stack, passive scanning and active transmission are two fundamentally different hardware states:

*   **Passive Beacon Reception:** The Wi-Fi card listens to beacon frames broadcast by access points. The signal appears strong because the physical proximity to the router allows for clear reception.
*   **Active State Negotiation:** Once "Connect" is clicked, NetworkManager and `wpa_supplicant` must exchange probe requests, perform the 4-way WPA cryptographic handshake, and execute DHCP leases.

If the wireless card can listen to beacons but fails to push active data frames onto the bus, the system remains stuck at "Connecting" before timing out.

## Part 2: Inspecting the Hardware and Active Kernel Modules

The first step in diagnosing any Linux wireless failure is identifying the exact PCI device ID and the running kernel driver.

```bash
lspci -nnk | grep -iA3 net
```

On this system, the output revealed:

```text
00:14.3 Network controller [0280]: Intel Corporation Alder Lake-P PCH CNVi WiFi [8086:51f0] (rev 01)
    Subsystem: Intel Corporation Single Band Wi-Fi 6(802.11ax) AX101 80MHz 1x1 [Harrison Peak] [8086:0244]
    Kernel driver in use: iwlwifi
    Kernel modules: iwlwifi
```

### Understanding Intel CNVi Architecture

The Intel AX101 is not a standalone discrete PCIe Wi-Fi card. It is a CNVi (Integrated Connectivity) solution:
*   The MAC logic and processor reside directly inside the Intel Alder Lake CPU/PCH.
*   The physical M.2 module (Harrison Peak) contains only the analog companion RF (CRF) transceiver.

Because the system bus is deeply integrated into the CPU's power architecture, aggressive Power Management, Active State Power Management (ASPM), and kernel mismatches can cause communication between the CPU and the CRF chip to lock up entirely.

## Part 3: Reading the Kernel Crash

Checking the live kernel ring buffer via `dmesg` reveals the root cause:

```bash
sudo dmesg | grep -iE 'iwlwifi|wlan' | tail -n 25
```

The system printed a loop of driver errors:

```text
[   8.253806] iwlwifi 0000:00:14.3: Microcode SW error detected. Restarting 0x0.
[   8.254384] iwlwifi 0000:00:14.3: 0x00000B03 | IML/ROM error/state
[   8.254535] iwlwifi 0000:00:14.3: 0x60000000 | FSEQ_ERROR_CODE
[   8.698493] iwlwifi 0000:00:14.3: Device error - SW reset
[   9.577066] iwlwifi 0000:00:14.3: LED command failed: -5
[   9.597319] iwlwifi 0000:00:14.3: Failed to send LINK_CONFIG_CMD (action:3): -5
[   9.597514] iwlwifi 0000:00:14.3: Failed to send flush command (-5)
[   9.597601] iwlwifi 0000:00:14.3: PHY ctxt cmd error. ret=-5
[ 148.544474] iwlwifi 0000:00:14.3: Scan failed! ret -5
```

### What These Errors Mean

*   **Microcode SW error detected & 0x00000B03:** The proprietary Intel firmware binary (e.g., `so-a0-hr-b0-89.ucode`) crashed inside the onboard microcontroller. When the firmware crashes, the radio enters a hardware halt.
*   **ret -5 (-EIO):** In Linux, `-5` represents an Input/Output error. The kernel module (`iwlmvm`) dispatched a link configuration or scan command, but because the firmware had crashed or was stuck in low-power bus sleep, the card never acknowledged the command.
*   **Rapid Scan Loops:** Because NetworkManager did not receive confirmation, it retried every second, saturating the unacknowledged CNVi queue until the connection aborted.

## Part 4: The Pitfall of Missing Firmware

During troubleshooting, moving the buggy `-89.ucode` firmware binary away resulted in:

```text
iwlwifi 0000:00:14.3: Direct firmware load for iwlwifi-so-a0-hr-b0-89.ucode failed with error -2
```

In Linux system calls, error `-2` is `-ENOENT` (No such file or directory). Because Linux distributions often carry only the single latest binary for newer CNVi chipsets, removing version 89 without having a fallback (like `-84` or `-77`) left the driver with zero firmware to load, rendering the hardware completely inert. The solution is to restore the binary and control the driver’s operational profile through kernel module options instead.

## Part 5: The Full Solution Stack

To get the Intel AX101 working reliably on Linux Mint, four layers must be configured: module parameters, hardware register discharge, NetworkManager power management, and connectivity watchdog handling.

### 1. Tune iwlwifi Module Parameters

Configure the driver to bypass buggy 802.11ax microcode execution paths, turn off low-power PCIe bus drops, and offload crypto back to the CPU.

Create or edit `/etc/modprobe.d/iwlwifi.conf`:

```bash
sudo xed /etc/modprobe.d/iwlwifi.conf
```

Paste the following configuration:

```text
# Force 802.11ac to bypass 802.11ax microcode execution panics on 1x1 antennas
options iwlwifi 11n_disable=8

# Use software crypto to prevent -EIO handshake drops during WPA exchanges
options iwlwifi swcrypto=1

# Disable PCIe bus sleep, U-APSD, and low-power D0i3 states
options iwlwifi power_save=0
options iwlwifi uapsd_disable=1
options iwlwifi d0i3_disable=1
options iwlwifi amsdu_size_8k=0

# Ensure Intel MVM subsystem runs in continuous active power mode
options iwlmvm power_scheme=1
```

Rebuild the initial ramdisk to apply these options at early boot:

```bash
sudo update-initramfs -u
```

### 2. Perform a True Hardware Cold Drain

Intel CNVi hardware stays energized in low-power sleep across soft reboots, so the `0x00000B03` error state will survive standard `sudo reboot` calls.

1.  Power off the laptop: `sudo poweroff`.
2.  Unplug the AC charger.
3.  Hold down the physical power button for 30–45 seconds.
4.  Release the button, reconnect power, and boot the machine.

This forces the CNVi internal registers to wipe clean and perform a true cold boot. For dual-boot users, Windows Fast Startup must be disabled in the Windows Control Panel, as it leaves the Wi-Fi card in a proprietary sleep state that bricks the Linux driver upon warm reboot.

### 3. Stop NetworkManager from Self-Terminating the Interface

Once the handshake succeeds, the connection may drop and shut down the radio on its own due to NetworkManager behaviors.

#### A. The Online Connectivity Check Watchdog

NetworkManager pings an external endpoint immediately upon connecting. If local DNS resolution is slow, NetworkManager concludes the connection is broken and terminates it.

Disable this behavior by creating `/etc/NetworkManager/conf.d/20-connectivity.conf`:

```text
[connectivity]
enabled=false
```

#### B. NetworkManager Internal Wi-Fi Power Saving

NetworkManager implements its own power daemon independent of `iwlwifi`. Open `/etc/NetworkManager/conf.d/default-wifi-powersave-on.conf`:

```bash
sudo xed /etc/NetworkManager/conf.d/default-wifi-powersave-on.conf
```

Change:

```text
[connection]
wifi.powersave = 3
```

To:

```text
[connection]
wifi.powersave = 2
```

(Value `2` explicitly disables power saving; `3` enables it).

### 4. Apply Changes and Connect

Restart the networking stack to load all updated profiles:

```bash
sudo systemctl restart NetworkManager
```

Delete any stale, corrupted connection attempts:

```bash
nmcli connection delete "<Your_SSID_Name>"
```

Connect cleanly from the terminal or the Cinnamon system tray:

```bash
nmcli dev wifi connect "<Your_SSID_Name>" password "YOUR_PASSWORD"
```

## Conclusion and Key Takeaways

*   **100% Signal Does Not Mean a Working Radio:** Passive reception of router beacon frames can work even when the card's active transmission queue is completely dead.
*   **ret -5 is a Microcode Bus Halt:** When `iwlwifi` throws error `-5` (-EIO), the card firmware has locked up. Look at your module parameters, PCIe ASPM, and low-power states (`d0i3`).
*   **CNVi Cards Require Cold Drains:** Modern integrated Wi-Fi transceivers maintain state across software reboots. A 30-second power button hold is often required to flush bad hardware registers.
*   **Kernel Version Alignment:** Extremely new or mainline kernels often experience regressions with older ucode revisions. When running Linux Mint, staying on stable LTS kernels ensures firmware and driver compatibility.

## References

Intel Wireless Wi-Fi Link Software
https://www.intel.com/content/www/us/en/support/articles/000005511/network-and-i-o/wireless.html

Linux Kernel Wireless Documentation
https://wireless.wiki.kernel.org/

iwlwifi Driver Project Page
https://wireless.wiki.kernel.org/users/drivers/iwlwifi