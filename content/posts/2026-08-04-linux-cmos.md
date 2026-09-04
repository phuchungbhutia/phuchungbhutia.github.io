---
title: "Bypassing CMOS Clock Failure on Linux with Automated Network Time Sync"
date: 2026-08-04
categories: ["Linux", "System Administration"]
tags: ["systemd", "NTP", "Hardware Troubleshooting", "Bash", "Linux Mint"]
---

## Overview

A depleted or faulty CMOS battery causes system clocks to reset to an epoch date (e.g., January 1, 1970) upon every power cycle. On modern Linux distributions, an incorrect system time breaks SSL/TLS certificate validation, systemd timers, package manager operations, and secure web browsing.

While replacing the motherboard RTC battery is the ideal physical fix, system-level automation provides an immediate software workaround by forcing network time synchronization immediately after the network interface comes online.

## The Solution Strategy

The default `systemd-timesyncd` or `chrony` services often fail to synchronize when system time is drastically skewed because huge time jumps are rejected by default security guardrails. To overcome this:

1. Unmask and force an instant step-update via NTP.
2. Bind the synchronization script to system network availability using a `systemd` unit file.
3. Fall back to HTTPS header date extraction if UDP NTP ports (port 123) are blocked by strict firewalls.

## Step 1: Writing the Synchronization Script

Create a script at `/usr/local/bin/force-time-sync.sh`:

```bash
#!/usr/bin/env bash
# Force-sync system time on boot despite extreme hardware clock skew

TARGET_NTP="pool.ntp.org"

echo "Attempting force-sync with $TARGET_NTP..."

# Stop timesyncd to release socket
systemctl stop systemd-timesyncd

# Step time forcefully using chrony or sntp
if command -v chronyd &> /dev/null; then
    chronyd -q "server $TARGET_NTP iburst"
elif command -v sntp &> /dev/null; then
    sntp -s $TARGET_NTP
else
    # Fallback: Extract UTC time from HTTP response header if NTP is blocked
    HTTP_DATE=$(curl -sI https://google.com | grep -i '^date:' | cut -d' ' -f2-)
    if [ -n "$HTTP_DATE" ]; then
        date -s "$HTTP_DATE"
    fi
fi

# Restart timesyncd service to maintain steady sync
systemctl start systemd-timesyncd
hwclock --systohc

```

Make the script executable:

```bash
sudo chmod +x /usr/local/bin/force-time-sync.sh

```

## Step 2: Creating the systemd Boot Service

Create `/etc/systemd/system/force-time-sync.service`:

```ini
[Unit]
Description=Force Network Time Sync on Boot (CMOS Skew Fix)
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/force-time-sync.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target

```

Enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable force-time-sync.service

```

This configuration ensures your OS clock synchronizes cleanly before desktop environments and background services initialize, completely mitigating system instability caused by hardware RTC failures.

---

# Maximizing Performance on 4GB RAM: Linux Mint & Manjaro XFCE Optimization Guide

---

## title: "Maximizing Performance on 4GB RAM: Linux Mint & Manjaro XFCE Optimization Guide"
date: 2026-08-04
categories: ["Linux", "Performance Tuning"]
tags: ["XFCE", "RAM Management", "Linux Mint", "Manjaro", "zram", "sysctl"]

## Overview

Running modern desktop Linux on systems with 4GB of RAM requires deliberate resource management. While XFCE is inherently lightweight, modern web browsers and multi-tasking demands can easily push low-spec hardware into severe disk thrashing (swap lockup).

By optimizing memory management policies, configuring compressed RAM swap (zram), and stripping unnecessary background daemons, a 4GB system can operate smoothly without UI lag.

## 1. Implement zram (Compressed Memory Swap)

`zram` creates a compressed block device in RAM that acts as swap space. It compresses memory pages on the fly using algorithms like `zstd`, effectively increasing available RAM capacity by 1.5x–2x at minimal CPU cost.

### On Arch / Manjaro:

```bash
sudo pacman -S zram-generator

```

Create `/etc/systemd/zram-generator.conf`:

```ini
[zram0]
zram-size = ram / 2
compression-algorithm = zstd

```

### On Debian / Linux Mint:

```bash
sudo apt install zram-tools

```

Edit `/etc/default/zramswap` and set:

```bash
ALGORITHM=zstd
PERCENT=50

```

Start the service:

```bash
sudo systemctl enable --now zramswap

```

## 2. Kernel Virtual Memory Tuning

Adjust Linux kernel swap behavior to favor RAM compression and reduce premature disk writes. Edit `/etc/sysctl.d/99-low-ram-optimization.conf`:

```ini
# Aggressively use swap space (ideal when zram is enabled)
vm.swappiness = 100

# Protect file system cache from being evicted too quickly
vm.vfs_cache_pressure = 50

# Smooth out dirty page flush behavior to prevent system freezes
vm.dirty_background_ratio = 5
vm.dirty_ratio = 10

```

Apply immediately:

```bash
sudo sysctl --system

```

## 3. Lightening the XFCE Environment

* **Disable Window Compositor Shadows:** Go to **Settings > Window Manager Tweaks > Compositor** and uncheck *Show shadows under pop-up windows* and *Show shadows under regular windows*.
* **Disable Startup Services:** Open **Session and Startup > Application Autostart** and uncheck unused daemons such as *Print Queue Applet*, *Update Managers* (switch to scheduled cron updates), and *Bluetooth Tray* (if unsupported).
* **Browser Optimization:** Use tab-suspending extensions (like *Auto Tab Discard*) and enable hardware acceleration in Firefox (`about:config` -> `gfx.webrender.all = true`).

---

# Extracting Financial Vouchers from eGramSwaraj to CSV Using Browser JavaScript

---

## title: "Extracting Financial Vouchers from eGramSwaraj to CSV Using Browser JavaScript"
date: 2026-08-04
categories: ["Data Extraction", "Automation"]
tags: ["JavaScript", "CSV", "eGramSwaraj", "Audit Automation", "Web Scraping"]

## Overview

Auditing local body financial records on portals like **eGramSwaraj** often involves navigating through nested HTML tables across hundreds of pages. Manually copying voucher details, receipt amounts, and action plan activity codes into spreadsheets is error-prone and time-consuming.

Using lightweight client-side JavaScript directly in the browser's Developer Console allows auditors to extract tabular accounting data and generate a downloadable `.csv` file instantly without installing external scraping software.

## The Browser Console Extraction Script

Navigate to the target voucher summary page on the eGramSwaraj portal, open your browser tools (**F12** or `Ctrl + Shift + I`), switch to the **Console** tab, and run the script below:

```javascript
(() => {
    // Select target data table containing voucher records
    const table = document.querySelector("table.table-bordered") || document.querySelector("table");
    if (!table) {
        console.error("No valid voucher data table found on this page.");
        return;
    }

    let csvContent = "";
    const rows = table.querySelectorAll("tr");

    rows.forEach(row => {
        const rowData = [];
        // Extract headers and data cells
        const cols = row.querySelectorAll("th, td");
        
        cols.forEach(col => {
            // Clean text: remove tabs, newlines, and trailing spaces
            let text = col.innerText.replace(/(\r\n|\n|\r)/gm, " ").replace(/\s+/g, " ").trim();
            // Escape double quotes inside values
            text = text.replace(/"/g, '""');
            // Wrap string in quotes to prevent delimiter breaking
            rowData.push(`"${text}"`);
        });

        if (rowData.length > 0) {
            csvContent += rowData.join(",") + "\n";
        }
    });

    // Trigger CSV download in browser
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    
    // Generate filename based on date and page title
    const filename = `eGramSwaraj_Vouchers_${new Date().toISOString().slice(0,10)}.csv`;
    link.setAttribute("href", url);
    link.setAttribute("download", filename);
    link.style.visibility = "hidden";
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    console.log(`Successfully exported ${rows.length} rows to ${filename}`);
})();

```

## Key Benefits for Auditing Workflows

| Aspect | Manual Copying | Client-Side JS Script |
| --- | --- | --- |
| **Speed** | 15–30 minutes per page | Under 2 seconds |
| **Accuracy** | High human error rate | 100% exact DOM parsing |
| **Formatting** | Misaligned columns | Uniform CSV standards |
| **Dependencies** | Spreadsheet software | Any modern web browser |

---

# Joplin vs. Obsidian for Local Government Audit Management and Reporting

---

## title: "Joplin vs. Obsidian for Local Government Audit Management and Reporting"
date: 2026-08-04
categories: ["Productivity", "Audit Management"]
tags: ["Joplin", "Obsidian", "Markdown", "Documentation", "Workflow"]

## Overview

Maintaining field notes, statutory provisions (such as state Audit Acts and CAG mandates), observation drafts, and RTI disclosures requires a robust knowledge management tool. Both **Joplin** and **Obsidian** are popular open-source or local-first Markdown tools, but their core architectures cater to different operational styles in professional auditing.

## Feature Breakdown

| Feature | Joplin | Obsidian |
| --- | --- | --- |
| **Storage Architecture** | SQLite database with internal file mapping | Pure plain-text `.md` files in a local folder ("Vault") |
| **Linking Style** | Traditional hierarchical folders & tags | Bi-directional links (`[[Note]]`) and Graph View |
| **PDF & Evidence Handling** | Native inline PDF preview and robust attachment indexing | Excellent file embedding with canvas integration |
| **Encryption** | Native End-to-End Encryption (E2EE) built-in | Requires third-party tools or paid sync for encryption |
| **Mobile Syncing** | Free via WebDAV, Nextcloud, Dropbox, or OneDrive | Free via Git/third-party sync; official paid Obsidian Sync |

## Joplin: Built for Structured Field Auditing

Joplin excels when your primary goal is organizing structured audit files into distinct notebooks (e.g., *Gram Panchayat Audits > 2025-26 > Financial Statements*).

* **Strengths:** Excellent web-clipper for archiving official government circulars, seamless E2EE across field devices, and strong built-in task list management.
* **Best Used For:** Standardized audit checklists, managing scanned voucher evidence, and maintaining strict hierarchical file trees.

## Obsidian: Built for Complex Compliance & Pattern Analysis

Obsidian shines when working with interconnected regulatory frameworks—such as cross-referencing specific CAMPA fund guidelines against recurring audit observations across multiple local bodies.

* **Strengths:** The graph view visualizes linkages between different audit teams, recurring financial irregularities, and statutory clauses. Because notes remain plain Markdown files on disk, they can easily be processed by custom Python scripts or command-line tools like `grep`.
* **Best Used For:** Drafting extensive audit reports, mapping statutory compliance networks, and building an interconnected audit knowledge base over years of service.
