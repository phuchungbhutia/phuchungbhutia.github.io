---
title: "Building the eGramSwaraj Audit Toolkit: From Scraping Messy Public Financial Data to Standardized Audit Reports"
date: "2026-08-04"
categories: ["Data Engineering", "Audit Automation", "Python", "JavaScript"]
tags: ["eGramSwaraj", "Web Scraping", "Pandas", "Regex", "Bookmarklet", "GovTech", "Audit"]
---

# Building the eGramSwaraj Audit Toolkit: From Scraping Messy Public Financial Data to Standardized Audit Reports

Local Fund Audit (LFA) departments and government auditors often face a steep technical challenge when reviewing public financial data from portals like India's **eGramSwaraj**. While the web portal hosts critical details regarding Gram Panchayat Development Plan (GPDP) expenditure, receipts, profiles, and vouchers, the data presentation on-screen is fragmented, vertical, and unstructured.

In this deep dive, we will walk through the step-by-step engineering process of capturing raw web data via browser bookmarklets, handling messy multi-line CSVs with custom Python regex parsers, and mapping vertical data into a horizontal, audit-ready 18-column master sheet.

---

## The Core Data Dilemma

When web-scraping eGramSwaraj voucher details, a single financial voucher does not export cleanly as a single row. Instead, the portal renders nested tables and vertical field-value pairs. 

### Why Standard Scraping Breaks Down
1. **Vertical "Staircasing":** A standard table reader sees headers like `Scheme Name` and values like `XV Finance Commission` spread across multiple rows or misaligned columns.
2. **Dual-Schema Structure:** Money coming in (**Receipt Vouchers**) contains completely different fields (e.g., *Grant Head, Instrument Type, Bank Account*) compared to money going out (**Payment Vouchers**, which contain *Expenditure Head, Activity Code, Payee Name, PFMS Details*).
3. **Multi-Payee Payments:** A single payment voucher (e.g., `XVFC/2025-26/P/1`) may execute payments to four different individuals or contractors (e.g., *Assistant Engineer, DPO, local suppliers*). Flattening this incorrectly results in lost payee names or inaccurate transaction totals.

---

## Phase 1: Browser-Based Data Extraction (Bookmarklets)

To scrape data without installing heavy automation frameworks like Selenium or Playwright, we leverage **JavaScript Bookmarklets**. These execute directly within the authenticated browser context.

### 1. Profile Scraper Bookmarklet (`profile_scraper.js`)
Captures Gram Panchayat administrative details cleanly in a two-column key-value format without falling into recursive row-sliding duplicates:

```javascript
javascript:(function(){
    console.log("🚀 Extracting Profile...");
    let csvContent = "Attribute,Details\n";
    const rows = document.querySelectorAll('#profileReportForm tr');
    rows.forEach(row => {
        const header = row.querySelector('th');
        const data = row.querySelector('td');
        if(header && data && !row.id.includes('heading')){
            let attr = header.innerText.trim().replace(/[:\n\t]/g,' ').replace(/\s+/g,' ');
            let detail = data.innerText.trim().replace(/"/g,'""').replace(/\s+/g,' ');
            if(attr && detail) csvContent += `"${attr}","${detail}"\n`;
        }
    });
    const blob = new Blob([csvContent], {type: "text/csv;charset=utf-8;"});
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "panchayat_profile.csv";
    link.click();
})();

```

### 2. Deep Accounts Scraper (`deep_accounts.js`)

Run from the **Monthly Wise Voucher Summary** page, this script recursively fetches voucher sub-links in the background with a 150ms delay to respect server rate limits (preventing HTTP `403 Forbidden` session timeouts):

```javascript
javascript:(function(){(async function(){
    console.log("🚀 Starting Deep Extraction...");
    let csv = "Month,Type,VoucherID,Data\n";
    const urlParams = new URLSearchParams(window.location.search);
    let gpuNo = urlParams.get('localBodyCode') || "Unknown";
    let links = Array.from(document.querySelectorAll('a[href*="voucherWiseReport.do"]')).map(a=>({m:a.innerText.trim(),u:a.href}));
    
    for(let m of links){
        console.log(`Scraping: ${m.m}`);
        let p = await fetch(m.u,{credentials:"include"}).then(r=>r.text());
        let d = (new DOMParser()).parseFromString(p,"text/html");
        let vL = Array.from(d.querySelectorAll('a[href*="VoucherDetail.do"]')).map(a=>({i:a.innerText.trim(),u:a.href,t:a.href.includes("payment")?"Payment":"Receipt"}));
        for(let v of vL){
            let vp = await fetch(v.u,{credentials:"include"}).then(r=>r.text());
            let vd = (new DOMParser()).parseFromString(vp,"text/html");
            let rows = Array.from(vd.querySelectorAll('table tr')).map(tr=>Array.from(tr.querySelectorAll('td,th')).map(td=>`"${td.innerText.trim().replace(/"/g,'""')}"`).join(','));
            rows.forEach(r=>{ if(r.length>20) csv+=`"${m.m}","${v.t}","${v.i}",${r}\n` });
            await new Promise(s=>setTimeout(s,150));
        }
    }
    let b = new Blob([csv],{type:"text/csv;charset=utf-8;"});
    let l = document.createElement("a");
    l.href = URL.createObjectURL(b);
    l.download = `accounts-${gpuNo}-2025-2026.csv`;
    l.click();
})()})();

```

---

## Phase 2: Python Data Cleaning & Grouping Logic

Once the raw CSV (`accounts-<GPU>-<FY>.csv`) is downloaded, we process it using Python and Pandas.

### Standardizing the 18 Audit Headers

To ensure full audit compliance, every row must standardize to an 18-column horizontal master structure:

1. **Core Headers:** `Month`, `Type`, `VoucherID`, `Date`, `Scheme`, `Particulars`
2. **Receipt Headers:** `Receipt Head`, `Received In`, `Bank Account No`, `Instrument Type`, `Instrument No`, `Receipt Amount`
3. **Payment Headers:** `Account Head`, `Activity Code`, `Mode of Payment`, `Payee Name`, `Payee Bank Details`, `Payment Amount`

### Complete Cleaning Script (`audit_master.py`)

```python
import csv
import re
import pandas as pd
import glob

def clean_txt(val):
    if not val:
        return ""
    val = re.sub(r'[\t\n\r]', ' ', str(val))
    return re.sub(r'\s+', ' ', val).strip()

def get_amt(val):
    val = str(val).replace(',', '')
    match = re.search(r'(\d+\.\d+|\d+)', val)
    return float(match.group(1)) if match else 0.0

def process_audit_files():
    files = glob.glob("accounts-*.csv")
    for f_name in files:
        # Pass 1: Group multi-line raw rows by unique VoucherID
        v_groups = {}
        with open(f_name, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            try:
                next(reader)
            except StopIteration:
                continue
                
            for row in reader:
                if not row or len(row) < 4 or "Report generated" in "".join(row):
                    continue
                vid = row[2].strip()
                if vid not in v_groups:
                    v_groups[vid] = {'Month': row[0], 'Type': row[1], 'rows': []}
                v_groups[vid]['rows'].append([clean_txt(c) for c in row[3:]])

        final_rows = []

        # Pass 2: Extract metadata and map schema
        for vid, group in v_groups.items():
            v_type, month = group['Type'], group['Month']
            full_txt = " ".join([" ".join(r) for r in group['rows']])
            
            # Common Metadata
            date = ""
            d_match = re.search(r'(\d{1,2}/\d{1,2}/\d{4})', full_txt)
            if d_match:
                date = d_match.group(1)
                
            scheme = ""
            if 'Scheme/Own Resources' in full_txt:
                scheme = full_txt.split('Resources :')[-1].split('Voucher')[0].strip()
            elif 'Scheme Name' in full_txt:
                scheme = full_txt.split('Scheme Name')[-1].split('Voucher')[0].strip()

            particulars = ""
            if 'Particulars :' in full_txt:
                particulars = full_txt.split('Particulars :')[-1].split('Activity')[0].split('Attached')[0].strip()

            if v_type == 'Payment':
                act_code = ""
                act_m = re.search(r'Activity Code\s*(\d+)', full_txt)
                if not act_m:
                    act_m = re.search(r'\b(\d{8,10})\b', full_txt)
                if act_m:
                    act_code = act_m.group(1)

                acc_head = ""
                for r in group['rows']:
                    r_txt = " ".join(r)
                    if 'Expenditure Heads' in r_txt:
                        acc_head = r_txt.replace('Expenditure Heads', '').replace(':', '').strip()

                # Extract individual payees for multi-payee vouchers
                payees = []
                for r in group['rows']:
                    r_txt = " ".join(r)
                    if any(x in r_txt for x in ["PFMS", "To Whom Paid", "Account No."]):
                        nm, bnk, amt = "Check Details", "", 0.0
                        for c in reversed(r):
                            val = get_amt(c)
                            if val > 0:
                                amt = val
                                break
                        if "Account No.:" in r_txt:
                            bnk = r_txt.split("Account No.:")[-1].strip()
                        if "PFMS" in r:
                            idx = r.index("PFMS")
                            if idx + 2 < len(r): nm = r[idx+2]
                        elif "To Whom Paid" in r:
                            idx = r.index("To Whom Paid")
                            if idx + 1 < len(r): nm = r[idx+1]
                        
                        if nm != "Check Details" or amt > 0:
                            payees.append({'nm': nm, 'bnk': bnk, 'amt': amt, 'mode': 'PFMS' if "PFMS" in r_txt else 'Advice'})

                if payees:
                    for p in payees:
                        final_rows.append({
                            'Month': month, 'Type': v_type, 'VoucherID': vid, 'Date': date, 'Scheme': scheme, 'Particulars': particulars,
                            'Receipt Head': '', 'Received In': '', 'Bank Account No': '', 'Instrument Type': '', 'Instrument No': '', 'Receipt Amount': '',
                            'Account Head': acc_head, 'Activity Code': act_code, 'Mode of Payment': p['mode'], 'Payee Name': p['nm'], 'Payee Bank Details': p['bnk'], 'Payment Amount': p['amt']
                        })
                else:
                    p_amt = get_amt(full_txt.split('Amount')[-1]) if 'Amount' in full_txt else 0.0
                    final_rows.append({
                        'Month': month, 'Type': v_type, 'VoucherID': vid, 'Date': date, 'Scheme': scheme, 'Particulars': particulars,
                        'Receipt Head': '', 'Received In': '', 'Bank Account No': '', 'Instrument Type': '', 'Instrument No': '', 'Receipt Amount': '',
                        'Account Head': acc_head, 'Activity Code': act_code, 'Mode of Payment': '', 'Payee Name': '', 'Payee Bank Details': '', 'Payment Amount': p_amt
                    })

            else:  # Receipt Vouchers
                r_head, r_in, bank_no, instr_type, instr_no, r_amt = "", "", "", "", "", 0.0
                for r in group['rows']:
                    r_txt = " ".join(r)
                    if any(x in r_txt for x in ['Expenditure Heads', 'Receipt Heads']):
                        r_head = r_txt.replace('Expenditure Heads', '').replace('Receipt Heads', '').replace(':', '').strip()
                    if 'Received In' in r_txt: r_in = r_txt.split(':')[-1].strip()
                    if 'Label.BankAcNo' in r_txt: bank_no = r_txt.split(':')[-1].strip()
                    if 'Voucher Type' in r_txt: instr_type = r_txt.split(':')[-1].strip()
                    if 'Cheque No' in r_txt: instr_no = r_txt.split('No :')[-1].split('Date')[0].strip()
                    for c in r:
                        val = get_amt(c)
                        if val > r_amt: r_amt = val

                final_rows.append({
                    'Month': month, 'Type': v_type, 'VoucherID': vid, 'Date': date, 'Scheme': scheme, 'Particulars': particulars,
                    'Receipt Head': r_head, 'Received In': r_in, 'Bank Account No': bank_no, 'Instrument Type': instr_type, 'Instrument No': instr_no, 'Receipt Amount': r_amt,
                    'Account Head': '', 'Activity Code': '', 'Mode of Payment': '', 'Payee Name': 'N/A', 'Payee Bank Details': '', 'Payment Amount': ''
                })

        output_name = f"clean-{f_name}"
        pd.DataFrame(final_rows).drop_duplicates().to_csv(output_name, index=False)
        print(f"✅ Created horizontal audit report: {output_name}")

if __name__ == "__main__":
    process_audit_files()

```

---

## Output Transformation

By running the script over messy raw files, we achieve clean horizontal normalization:

### Input (Fragmented Web Data):

```csv
April, 2025, Payment, XVFC/2025-26/P/1, Expenditure Heads 2210 - Health, Amount, 95697
April, 2025, Payment, XVFC/2025-26/P/1, Mode Of Payment, PFMS, To Whom Paid, BANWARILALL OMKARMULL, 95697

```

### Output (`clean-accounts-300083-2025-2026.csv`):

| Month | Type | VoucherID | Date | Scheme | Particulars | Account Head | Activity Code | Mode of Payment | Payee Name | Payment Amount |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| April, 2025 | Payment | XVFC/2025-26/P/1 | 08/04/2025 | XV Finance Commission (Untied) | Repair Work | 2210 - Health and Family Welfare | 70735454 | PFMS | BANWARILALL OMKARMULL | 95697.0 |

---

## Open-Source GitHub Repository Architecture

To package this tool for auditor workflows, publish the repository using the following folder structure:

```text
egram-audit-toolkit/
├── assets/                # Banners, diagrams, and sample outputs
├── scrapers/              # Browser JavaScript scrapers & bookmarklets
│   ├── profile_scraper.js
│   └── deep_accounts.js
├── cleaning/              # Python transformation tools
│   └── audit_master.py
├── .gitignore             # Ignore raw csv files & __pycache__
├── LICENSE                # MIT License
└── README.md              # Comprehensive project documentation

```

### `.gitignore` Setup

```text
# Ignore raw scraped accounts data
accounts-*.csv
deep_audit_raw.csv

# Ignore output CSVs during dev
clean-accounts-*.csv
standardized_accounts.csv

# Python cache
__pycache__/
*.pyc
.DS_Store

```

---

## Conclusion & Key Learnings

1. **Two-Pass In-Memory Aggregation:** Never parse fragmented public data row-by-row. Group rows into a dictionary by primary entity key (`VoucherID`) first, then extract text fields using Regex anchors.
2. **Handle Optional Multi-Row Records:** Payment vouchers often contain arrays of sub-transactions (multiple payees). Design the parser to append N rows per voucher when payees exist, or default to a single summary row when no payee list is found.
3. **Graceful Browser Throttling:** Client-side scrapers operating on government portals must include explicit pauses (`setTimeout(..., 150)`) between sub-page fetches to prevent session lockouts.

This tool reduces audit data preparation time from days of manual data entry down to seconds of automated processing!

```

```
