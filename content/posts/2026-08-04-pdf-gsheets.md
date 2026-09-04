---
title: "How to Fix Firefox Saving PDFs Instead of Printing in Google Sheets"
date: "2026-08-04T10:00:00+05:30"
categories: ["Tech Support", "Web Browsers", "Productivity"]
tags: ["Firefox", "Google Sheets", "Printing", "Troubleshooting", "PDF"]
---

If you frequently use Google Sheets inside Mozilla Firefox, you may have run into a frustrating issue: when you hit the "Print" button, Firefox downloads or prompts you to save a PDF file instead of sending the document straight to your physical printer. 

While this feels like a glitch, it is actually expected behavior based on how Google Sheets interacts with different browsers. Fortunately, there are several straightforward ways to fix this workflow.

---

### Why Does This Happen?

Unlike Google Chrome—which features a native, integrated print engine designed specifically for Google Workspace apps—Google Sheets treats Firefox differently. 

When you click **File > Print** or hit the **Print icon** within a Google Sheet, Google's servers render your spreadsheet layout into a standard PDF document. It then passes this generated PDF to Firefox. Depending on your browser's default download settings, Firefox simply saves the file to your disk rather than opening a print preview or routing it directly to your hardware printer.

---

### Method 1: Bypass the Google Print Button (Fastest Fix)

The easiest way to skip the unwanted PDF download is to trigger your system’s native print dialog directly, ignoring Google's built-in print pipeline altogether.

* **Windows / Linux:** Press `Ctrl` + `Shift` + `P`
* **Mac:** Press `Cmd` + `Option` + `P`

**Why this works:** Using this browser shortcut bypasses Google Sheets' PDF generator entirely and opens your operating system's standard print dialog instantly, allowing you to select your target printer right away.

---

### Method 2: Configure Firefox to Open PDFs Automatically

If you prefer using the standard print button inside Google Sheets, you can configure Firefox to open the PDF in a new browser tab immediately instead of prompting you to save it.

1. Open Firefox and click the **Menu button** (three horizontal lines) in the upper-right corner.
2. Select **Settings**.
3. Under the **General** panel, scroll down until you reach the **Applications** section.
4. Locate **Portable Document Format (PDF)** in the Content Type list.
5. Change the corresponding Action setting to **Open in Firefox**.

#### Bonus Step for Forced Downloads
Some web scripts force Firefox to download PDFs as attachments even when configured to preview them. To prevent this:
1. Open a new tab, type `about:config` in the address bar, and press Enter.
2. Accept the caution prompt.
3. Search for the preference: `browser.download.open_pdf_attachments_inline`
4. Toggle its value to **true**.

---

### Method 3: Clear Corrupted Printer Settings

If Firefox continues defaulting to "Save as PDF" even when the system print window opens, your internal browser printer settings may be stuck or corrupted.

1. Type `about:support` in your Firefox address bar and press Enter.
2. Scroll down to the **Printing** section near the bottom of the page.
3. Click the **Clear saved print settings** button.
4. Restart Firefox.

Upon restarting, Firefox will re-detect your operating system's default physical printer and reset all print preferences to default.

---

### Quick Comparison of Methods

| Method | Outcome | Best Used For |
| :--- | :--- | :--- |
| **`Ctrl` + `Shift` + `P`** | Direct to physical printer | Speed, bypassing PDF handling completely |
| **Open PDFs in Tab** | PDF opens in a new browser tab | Previewing layout before sending to printer |
| **Clear Print Settings** | Resets Firefox printer defaults | Resolving persistent "Save to PDF" bugs |

By adjusting these quick settings or using the browser print shortcut, you can restore a seamless, one-click printing experience from Google Sheets in Firefox.
