---
title: "Automating Sikkim Government Holidays and Recurring Saturdays in Google Calendar"
description: "Learn to generate and import a Google Calendar CSV for Sikkim gazetted holidays and recurring second and fourth Saturdays using Python."
date: 2026-11-18 12:00:00 +0000
categories: [Automation, Productivity, Python]
tags: [google-calendar, python, sikkim, csv, automation]
---

# Automating Sikkim Government Holidays and Recurring Saturdays in Google Calendar

Keeping track of state gazetted holidays, restricted leaves, and monthly non-working Saturdays should not require manually navigating a calendar PDF. Whether you work in a government department or plan your schedule around Sikkim's official calendar, you can build a reusable Google Calendar CSV import file in minutes. This guide covers the exact CSV schema Google Calendar expects, how to handle multi-day holidays, and the step-by-step import workflow.

## Understanding Google Calendar CSV Architecture

Google Calendar accepts `.csv` files for bulk event creation, provided the file uses specific case-sensitive header names and date conventions.

### Required and Optional CSV Headers

Your CSV header row must match these exact field names.

| Column Header | Required | Format and Accepted Values | Notes |
|---|---|---|---|
| `Subject` | Yes | Plain text | The title of the holiday or event. |
| `Start Date` | Yes | `MM/DD/YYYY` or `YYYY-MM-DD` | `01/15/2026` is the safest format across locales. |
| `Start Time` | No | `HH:MM AM/PM` | Leave blank for all-day events. |
| `End Date` | No | `MM/DD/YYYY` or `YYYY-MM-DD` | Exclusive for multi-day all-day events. |
| `End Time` | No | `HH:MM AM/PM` | Leave blank for all-day events. |
| `All Day Event` | No | `True` or `False` | Must be `True` for holiday almanacs. |
| `Description` | No | Plain text | Ideal for quoting government notification numbers. |
| `Location` | No | Plain text | Optional geographic tag. |
| `Private` | No | `True` or `False` | Use `False` if sharing the calendar with colleagues. |

### Crucial Google Calendar Quirks

> **Note:** Google Calendar CSV parsing has specific behaviors regarding date ranges and recurrence rules.

* **Exclusive End Dates for Multi-Day Events:** For single-day all-day events, set both `Start Date` and `End Date` to the same value. For multi-day stretches like Durga Puja, Google Calendar treats the `End Date` as exclusive. To make the banner span through October 23, set `End Date` to `10/24/2026`.
* **No Native RRULE Support in CSV:** The CSV parser does not support recurrence formulas. To make Second Saturday and Fourth Saturday populate automatically, you must pre-generate explicit rows for every month in your script or toggle recurrence manually in the UI.

## Generating the Almanac CSV via Python

You can use Python built-in libraries to compute every second and fourth Saturday automatically and merge them with the Home Department gazetted holiday list.

### Prerequisites

* Python 3.x installed.
* No external third-party packages required. Only standard library modules `csv`, `calendar`, and `datetime` are used.

### Complete Generator Script

Save the following code as `generate_sikkim_almanac.py` and run it in your terminal using `python3 generate_sikkim_almanac.py`.

```python
import calendar
import csv
import datetime

# Official Gazetted and Restricted Holidays
# Format: (Start YYYY-MM-DD, Inclusive End YYYY-MM-DD, Event Title, Notification Reference)
HOLIDAYS = [
    ("2026-01-01", "2026-01-01", "New Year's Day", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-01-15", "2026-01-15", "Maghe Sankranti", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-01-19", "2026-01-19", "Sonam Lochhar", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-01-26", "2026-01-26", "Republic Day", "National Holiday - Notification No. 89/Home/2025"),
    ("2026-02-18", "2026-02-18", "Losar", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-02-26", "2026-02-26", "Akhil Sikkim Khas Chettri Bahun Kalyan Sangh Foundation Day", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-03-03", "2026-03-03", "Bhumchu", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-03-04", "2026-03-04", "Holi", "Public Holiday - Revised via Notification No. 15/Home/2026"),
    ("2026-03-21", "2026-03-21", "Id-Ul-Fitr", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-03-27", "2026-03-27", "Ramnawami (Chaite Dasain)", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-04-03", "2026-04-03", "Good Friday", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-04-14", "2026-04-14", "Dr. B.R. Ambedkar Jayanti", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-05-01", "2026-05-01", "Shyadar Pidar", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-05-16", "2026-05-16", "State Day", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-05-31", "2026-05-31", "Saga Dawa", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-07-13", "2026-07-13", "Bhanu Jayanti", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-07-18", "2026-07-18", "Drukpa Tshe-zi", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-07-24", "2026-07-24", "Guru Rimpoche's Thungkar Tshechu", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-08-08", "2026-08-08", "Tendong Lho Rum Faat", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-08-15", "2026-08-15", "Independence Day", "National Holiday - Notification No. 89/Home/2025"),
    ("2026-08-20", "2026-08-20", "Nepali Bhasa Manyata Diwas", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-08-28", "2026-08-28", "Pang Lhabsol", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-09-04", "2026-09-04", "Janmashtami", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-09-14", "2026-09-14", "Teej (Haritalika)", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-09-25", "2026-09-25", "Indrajatra", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-10-02", "2026-10-02", "Gandhi Jayanti", "National Holiday - Notification No. 89/Home/2025"),
    ("2026-10-05", "2026-10-05", "Birthday of Late Nar Bahadur Bhandari", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-10-19", "2026-10-23", "Durga Puja (Dasain)", "Public Holiday (5 Days) - Notification No. 89/Home/2025"),
    ("2026-11-01", "2026-11-01", "Lhabab Duechen", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-11-09", "2026-11-11", "Laxmi Puja (Deepawali)", "Public Holiday (3 Days) - Notification No. 89/Home/2025"),
    ("2026-11-30", "2026-11-30", "Sakewa", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-12-07", "2026-12-07", "Kagyed Dance", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-12-09", "2026-12-14", "Losoong / Namsoong", "Public Holiday (6 Days) - Notification No. 89/Home/2025"),
    ("2026-12-15", "2026-12-15", "Chasok Tongnam / Nyengpa Guzom", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-12-16", "2026-12-16", "Nyengpa Guzom", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-12-23", "2026-12-23", "Puhgal Parim / Teyongsi Sirijunga Sawan Tongnam", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-12-25", "2026-12-25", "Christmas", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-12-28", "2026-12-28", "Barahimijong", "Public Holiday - Notification No. 89/Home/2025"),
    ("2026-12-30", "2026-12-30", "Tamu Lochar", "Public Holiday - Notification No. 89/Home/2025"),
]

events = []

# Process Gazetted Holidays (Adjusting End Date +1 day for multi-day blocks)
for start_str, end_str, title, desc in HOLIDAYS:
    s_dt = datetime.date.fromisoformat(start_str)
    e_dt = datetime.date.fromisoformat(end_str)
    cal_end = e_dt + datetime.timedelta(days=1) if e_dt > s_dt else s_dt
    events.append((s_dt, title, cal_end, desc))

# Compute 2nd and 4th Saturdays for every month across 2026 and 2027
for year in [2026, 2027]:
    for month in range(1, 13):
        weeks = calendar.monthcalendar(year, month)
        saturdays = [w[calendar.SATURDAY] for w in weeks if w[calendar.SATURDAY] != 0]
        
        sec_sat = datetime.date(year, month, saturdays[1])
        fourth_sat = datetime.date(year, month, saturdays[3])
        
        events.append((sec_sat, "Second Saturday (Govt Holiday)", sec_sat, "Monthly Second Saturday Holiday - Govt of Sikkim"))
        events.append((fourth_sat, "Fourth Saturday (Govt Holiday)", fourth_sat, "Monthly Fourth Saturday Holiday - Govt of Sikkim"))

# Sort chronologically and write UTF-8 CSV
events.sort(key=lambda x: (x[0], x[1]))

headers = ["Subject", "Start Date", "Start Time", "End Date", "End Time", "All Day Event", "Description", "Location", "Private"]

with open("sikkim_govt_holidays_google_calendar.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    for s_dt, title, e_dt, desc in events:
        writer.writerow([
            title,
            s_dt.strftime("%m/%d/%Y"),
            "",
            e_dt.strftime("%m/%d/%Y"),
            "",
            "True",
            desc,
            "Sikkim, India",
            "False"
        ])

print(f"Exported {len(events)} calendar events successfully.")
```

### Sample Output Structure

When opened in a spreadsheet editor or plain-text viewer, the generated `.csv` will resemble this structure.

```csv
Subject,Start Date,Start Time,End Date,End Time,All Day Event,Description,Location,Private
New Year's Day,01/01/2026,,01/01/2026,,True,Public Holiday - Notification No. 89/Home/2025,"Sikkim, India",False
Second Saturday (Govt Holiday),01/10/2026,,01/10/2026,,True,Monthly Second Saturday Holiday - Govt of Sikkim,"Sikkim, India",False
Maghe Sankranti,01/15/2026,,01/15/2026,,True,Public Holiday - Notification No. 89/Home/2025,"Sikkim, India",False
```

## Recommended Google Calendar Settings Before Importing

> **Note:** Never import bulk holiday files directly into your primary personal calendar. Creating a dedicated sub-calendar prevents tedious manual deletion if you need to update next year's notification or wipe duplicates.

* Open Google Calendar on a desktop web browser, as CSV import is unavailable in the mobile app.
* Locate **Other calendars** on the left sidebar and click the **Add other calendars** icon, then select **Create new calendar**.
* Configure the calendar details with the name `Sikkim Govt Holidays`, a relevant description, and the time zone `(GMT+05:30) India Standard Time - Kolkata`.
* Click **Create calendar**.
* Assign a distinct color to the new calendar via the three-dot menu so state holidays stand out from work meetings.

## Importing the CSV File into Google Calendar

* Click the **Settings** gear icon in the top-right corner and select **Settings**.
* Click **Import and export** in the left navigation menu.
* Under the **Import** section, click **Select file from your computer** and choose `sikkim_govt_holidays_google_calendar.csv`.
* Open the **Add to calendar** dropdown and select the `Sikkim Govt Holidays` sub-calendar.
* Click **Import** and verify the confirmation banner states the correct number of imported events.

## Setting Infinite Monthly Recurrence

If you want Second Saturday and Fourth Saturday to repeat indefinitely without re-importing future CSVs, follow these steps.

* Click any **Second Saturday (Govt Holiday)** event on your calendar and select the **Edit** icon.
* Below the date fields, click the **Does not repeat** dropdown and choose **Monthly on the second Saturday**.
* Click **Save**.
* Repeat the exact same step on a **Fourth Saturday (Govt Holiday)** event and set it to **Monthly on the fourth Saturday**.

## Troubleshooting Common CSV Import Errors

* **Imported zero events or date parsing failure:** Ensure your CSV saves dates in `MM/DD/YYYY` format. Excel may auto-reformat them, so edit CSV files in a plain-text editor or via Python.
* **Multi-day holidays ending one day early:** Verify that `End Date` is set to one day after the final holiday date whenever `All Day Event` is `True`.
* **Garbled characters in festival names:** Ensure the file is encoded in UTF-8 without BOM by using `encoding="utf-8"` in Python.

## Summary

* Google Calendar requires specific CSV headers and exclusive end dates for multi-day all-day events.
* Python standard libraries can automatically compute and format Second and Fourth Saturdays alongside official gazetted holidays.
* Importing into a dedicated sub-calendar protects your primary schedule and simplifies future updates.
* Manual UI adjustments are required for infinite monthly recurrence, as CSV files do not support native RRULE parsing.

## References

* [Google Calendar Help: Import events to Google Calendar](https://support.google.com/calendar/answer/37118)
* [Sikkim Home Department Official Notifications](https://sikkim.gov.in)