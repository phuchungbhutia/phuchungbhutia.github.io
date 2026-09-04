---
title: "Automating Contact Imports: How to Convert Complex Excel Spreadsheets to Google Contacts CSV"
date: "2026-08-04"
categories: ["Data Management", "Automation", "Productivity"]
tags: ["Python", "Pandas", "Google Contacts", "Excel", "Data Cleaning"]
---

Managing organizational contact directories can often get messy—especially when administrative data is scattered across multiple Excel spreadsheets, missing vital fields, or formatted strictly for internal reporting rather than contact management systems. 

When preparing contact directories for seamless mobile sync via **Google Contacts**, standard raw exports won't cut it. Google Contacts expects a precise, standardized CSV schema to map details like names, titles, phone numbers, and notes correctly.

---

### The Problem: Raw Spreadsheets vs. Google Contacts Schema

Standard office documents like `ADs(P).xlsx` or `PAAs.xlsx` usually organize information visually for humans rather than programmatically for software. They often feature:
* Heterogeneous layouts spread across multiple sheets.
* Non-standardized column names (e.g., `Contact No`, `Contact no`, `Name of ADs`, `Name of Sachiva`).
* Missing values (such as entries without contact numbers or complete missing datasets).
* Numbers that risk being formatted into scientific notation when opened in standard spreadsheet software (e.g., `9.733338e+09`).

To successfully import these records into Google Contacts without manual entry, you need to extract the raw records, filter out incomplete entries, normalize column schemas, and map them into Google's recognized format.

---

### Understanding the Google Contacts CSV Structure

Google Contacts reads standard CSV files but expects specific column headers to map data seamlessly into contact fields. While you can include a wide variety of attributes, the core framework relies on these key headers:

| Header Name | Description | Example Output |
| :--- | :--- | :--- |
| **Name** | Display name of the contact | `Mohan Kumar Rai` |
| **Given Name** | First name / Given name | `Mohan` |
| **Family Name** | Last name / Surname | `Kumar Rai` |
| **Phone 1 - Type** | Label for the primary phone number | `Mobile` |
| **Phone 1 - Value** | Clean, numerical contact string | `9733337954` |
| **Organization 1 - Name**| Associated department, GPU, or company | `Kongri Labdang` |
| **Organization 1 - Title**| Official position or job title | `Assistant Director` |
| **Group Membership** | Assigns contacts to default or custom groups | `* myContacts` |
| **Notes** | Contextual attributes (Districts, BACs, references) | `District: Gyalshing, BAC: Chongrong` |

---

### The Solution: Python & Pandas Conversion Workflow

Using Python and `pandas`, we can automate the parsing, cleaning, and formatting process. Here is how the end-to-end transformation script works:

#### Step 1: Loading and Cleaning Data Across Sheets

```python
import pandas as pd

# Load dataset sheets
ads1 = pd.read_csv('ADs(P) .xlsx - Sheet1.csv', skiprows=1)
ads2 = pd.read_csv('ADs(P) .xlsx - Sheet2.csv')

# Clean Sheet 1 (Assistant Directors)
ads1_clean = ads1[['Name of ADs', 'Contact No', 'Unnamed: 5', 'BAC', 'District']].copy()
ads1_clean.columns = ['Name', 'Phone', 'GPU', 'BAC', 'District']
ads1_clean['Title'] = 'Assistant Director'
ads1_clean = ads1_clean.dropna(subset=['Name', 'Phone'])

# Clean Sheet 2 (Sachivas)
ads2_clean = ads2[['Name of Sachiva', 'Contact no', 'Name of GPU', 'BAC', 'District']].copy()
ads2_clean.columns = ['Name', 'Phone', 'GPU', 'BAC', 'District']
ads2_clean['Title'] = 'Sachiva'
ads2_clean = ads2_clean.dropna(subset=['Name', 'Phone'])

# Combine sheets into a single workspace
contacts = pd.concat([ads1_clean, ads2_clean], ignore_index=True)

```

#### Step 2: Name Parsing & Phone Number Normalization

To ensure phone numbers do not degrade into scientific notation or floating-point numbers (`.0`), we apply direct string conversion functions before mapping.

```python
# Helper to split names cleanly into Given Name and Family Name
def split_name(name):
    parts = str(name).strip().split()
    given = parts[0] if len(parts) > 0 else ""
    family = " ".join(parts[1:]) if len(parts) > 1 else ""
    return given, family

# Helper to format phone values properly
def format_phone(val):
    try:
        s = str(val)
        if s.endswith('.0'):
            s = s[:-2]
        return str(int(float(val)))
    except:
        return str(val).strip()

names_split = contacts['Name'].apply(split_name)

```

#### Step 3: Mapping to Google Contacts Schema

```python
google_contacts = pd.DataFrame()

# Standard Field Mappings
google_contacts['Name'] = contacts['Name']
google_contacts['Given Name'] = [x[0] for x in names_split]
google_contacts['Family Name'] = [x[1] for x in names_split]
google_contacts['Group Membership'] = '* myContacts'
google_contacts['Phone 1 - Type'] = 'Mobile'
google_contacts['Phone 1 - Value'] = contacts['Phone'].apply(format_phone)
google_contacts['Organization 1 - Name'] = contacts['GPU']
google_contacts['Organization 1 - Title'] = contacts['Title']

# Packing metadata into the Notes column
google_contacts['Notes'] = "District: " + contacts['District'].fillna('') + ", BAC: " + contacts['BAC'].fillna('')

# Remove duplicates & export
google_contacts = google_contacts.drop_duplicates()
google_contacts.to_csv('google_contacts.csv', index=False)

```

---

### How to Import the Output File into Google Contacts

Once the script generates `google_contacts.csv`, importing it to your account takes just a few clicks:

1. Navigate to [Google Contacts](https://contacts.google.com).
2. On the left sidebar menu, click **Import**.
3. Click **Select file** and choose the newly generated `google_contacts.csv`.
4. Click **Import**. Google Contacts will automatically parse the headers and populate all fields, labels, and notes instantly across your synced mobile devices.

```

```
