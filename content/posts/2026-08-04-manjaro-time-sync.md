---
title: "Bypassing Faulty CMOS Batteries in Linux Mint and Manjaro with Automated Network Time Sync"
date: "2026-08-04T10:00:00+05:30"
categories: ["Linux", "System Administration"]
tags: ["linux-mint", "manjaro", "systemd", "ntp", "cmos", "bash-scripting", "troubleshooting"]
---

Dealing with a faulty or dead motherboard CMOS battery can be a frustrating experience on Linux systems. Every cold boot resets the system clock—often back to 2010 or 1970—causing broken SSL/TLS certificates, failing web browsers, broken package manager updates, and out-of-sync system logs.

While replacing the CR2032 battery is the hardware fix, you can completely automate the recovery process in software so your computer seamlessly adjusts to the correct local time within seconds of booting up.

Here is a step-by-step technical breakdown of how we solved this issue on **Manjaro** and **Linux Mint**, along with the exact troubleshooting steps to prevent common systemd errors.

---

## 1. Understanding the Core Problem

When a system boots with a dead CMOS battery:
1. **Hardware Clock (RTC) Resets:** The motherboard's Real-Time Clock loses power and defaults to a base era date.
2. **Linux Trust Failure:** Default time synchronization utilities (like `systemd-timesyncd`) often refuse to sync if the gap between the hardware clock and current reality exceeds a specific safety threshold (the "panic threshold").
3. **Network Delays:** Automatic synchronization fails if `systemd-timesyncd` fires before Wi-Fi or Ethernet interfaces establish an active internet connection.

To bypass this permanently, we construct a lightweight startup script that waits for an active internet connection, forces an immediate jump using an explicit NTP server (`time.nic.in` / `164.100.255.122`), and updates the RTC mode to UTC.

---

## 2. Setting Up the Automated Time-Sync Script

We write a robust shell script at `/usr/local/bin/fix-clock.sh` that polls the network connection before triggering the forced time leap.

### Step-by-Step Implementation

1. Open your terminal and create the script cleanly using `cat` to prevent copy-paste character formatting issues:

```bash
sudo bash -c 'cat << "EOF" > /usr/local/bin/fix-clock.sh
#!/bin/bash
# Wait up to 20 seconds for an active internet connection
for i in {1..20}; do
    if ping -c 1 8.8.8.8 &>/dev/null; then
        # 1. Force network sync using a reliable NTP server
        sudo ntpdate -u time.nic.in
        
        # 2. Temporarily disable NTP to allow system adjustments
        sudo timedatectl set-ntp false
        
        # 3. Force Real-Time Clock (RTC) to UTC mode for stability on dead hardware
        sudo timedatectl set-local-rtc 0
        
        # 4. Re-enable automatic sync (forces systemd to align hardware and system clocks)
        sudo timedatectl set-ntp true
        
        exit 0
    fi
    sleep 1
done
exit 1
EOF'

```

2. Make the script executable and set strict file permissions:

```bash
sudo chmod +x /usr/local/bin/fix-clock.sh
sudo chmod 755 /usr/local/bin/fix-clock.sh

```

---

## 3. Creating the Systemd Service

To ensure this script fires automatically on every system boot, we wrap it in a systemd service unit file.

1. Create `/etc/systemd/system/fix-cmos.service`:

```ini
[Unit]
Description=Force Time Sync on Boot for Faulty CMOS
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/fix-clock.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target

```

2. Register and enable the service:

```bash
# Reload systemd configuration
sudo systemctl daemon-reload

# Enable service to start automatically on boot
sudo systemctl enable fix-cmos.service

# Trigger service manually to test execution
sudo systemctl start fix-cmos.service

```

---

## 4. Key Troubleshooting Points and Solutions

During setup, several common errors may occur depending on distribution releases and system configurations. Here is how to fix each one:

### A. Error: `status=203/EXEC`

* **Symptom:** `systemctl status fix-cmos.service` reports `Active: failed (Result: exit-code)` with `status=203/EXEC`.
* **Cause:** Missing executable permissions or hidden Windows-style line endings (`\r\n`) introduced during copy-pasting.
* **Fix:**
```bash
sudo sed -i -e 's/\r$//' /usr/local/bin/fix-clock.sh
sudo chmod +x /usr/local/bin/fix-clock.sh

```



### B. Error: `hwclock: command not found`

* **Symptom:** Modern distros like Linux Mint omit legacy utilities like `hwclock`.
* **Fix:** Replace `hwclock --systohc` calls with `timedatectl` toggles:
```bash
sudo timedatectl set-ntp false
sudo timedatectl set-ntp true

```


Toggling NTP forces `systemd-timesyncd` to automatically update the hardware clock without relying on legacy tools.

### C. Error: `Failed to set time: Automatic time synchronization is enabled`

* **Symptom:** `timedatectl set-time` fails when running directly in terminal.
* **Fix:** Always disable NTP before attempting manual clock overrides, then re-enable it immediately after:
```bash
sudo timedatectl set-ntp false
# Perform adjustments here
sudo timedatectl set-ntp true

```



### D. RTC in Local Time Zone Mismatch

* **Symptom:** Hardware clock drifts or jumps unexpectedly across restarts when dual-booting or when CMOS resets.
* **Fix:** Keep the hardware clock locked to UTC:
```bash
sudo timedatectl set-local-rtc 0

```



---

## 5. Verification

After completing the setup, verify the system status using `timedatectl status`:

```bash
timedatectl status

```

**Expected Successful Output:**

```text
               Local time: Tue 2026-08-04 19:20:18 IST
           Universal time: Tue 2026-08-04 13:50:18 UTC
                 RTC time: Tue 2026-08-04 13:50:18
                Time zone: Asia/Kolkata (IST, +0530)
System clock synchronized: yes
              NTP service: active
          RTC in local TZ: no

```

### Summary of Final Configuration

| Parameter | Desired State | Purpose |
| --- | --- | --- |
| **System clock synchronized** | `yes` | Validates active handshake with network time servers |
| **NTP service** | `active` | Keeps system time accurate in background |
| **RTC in local TZ** | `no` | Keeps motherboard hardware clock in UTC mode |

With this setup active, both Linux Mint and Manjaro systems will quietly poll for internet connectivity at boot, force time alignment via reliable NTP servers, and keep your clock synced regardless of motherboard hardware failures.

```
