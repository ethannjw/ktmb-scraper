# Logrotate Setup for KTMB Scraper

This document explains how to configure logrotate to automatically manage and clean up old logs for the KTMB Scraper project.

## Why Use Logrotate?
Continuous logging can quickly fill your storage. Logrotate automatically rotates, compresses, and deletes old logs so you don't have to manage them manually.

---

## Step 1: Install Logrotate (if needed)
On most Linux systems, logrotate is pre-installed. To install or make sure it is installed, run:

```bash
sudo apt update
sudo apt install logrotate
```

---

## Step 2: Create a Logrotate Config for KTMB Scraper

1. **Identify your log file path** (e.g., `/home/<user>/apps/ktmb-scraper/ktmb-scraper/logs/ktmb_scraper.log`).
2. **Create config file** (as root or using sudo):

```bash
sudo nano /etc/logrotate.d/ktmb-scraper
```

Paste the following (replace the path with your actual log location):

```bash
/home/<user>/apps/ktmb-scraper/ktmb-scraper/logs/ktmb_scraper.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    copytruncate
}
```

**Explanation of options:**
- `daily`: Rotate the log every day.
- `rotate 7`: Keep 7 old logs, delete older ones.
- `compress`: Compress old log files to save space.
- `missingok`: Don’t error if the log is missing.
- `notifempty`: Don’t rotate if the log is empty.
- `copytruncate`: Truncate the log file in place after copying it (for programs that keep files open while writing).

---

## Step 3: Test Your Logrotate Configuration

Run logrotate manually to make sure it works:

```bash
sudo logrotate --debug /etc/logrotate.d/ktmb-scraper
```

To force rotation (for testing):

```bash
sudo logrotate -f /etc/logrotate.d/ktmb-scraper
```

---

## Step 4: Automatic Rotation via Cron
Logrotate is normally run daily via cron automatically (no setup needed). Your config will be read with the system's daily schedule.

---

## FAQs & Troubleshooting

**Q: Does `rotate 7` mean 7 lines?**  
A: No, it keeps 7 *log files* (archives), not lines. Each archive covers a rotation period, so you effectively keep, for example, 7 days of logs if rotating daily.

**Q: Where are rotated logs?**  
A: In the same directory, named like `ktmb_scraper.log.1.gz`, `ktmb_scraper.log.2.gz`, etc.

**Q: Nothing happens when I run logrotate?**  
A: Check that your log file path is correct, and that your user has read/write permissions. Add `create` option if you want logrotate to create a new file after rotation (most use `copytruncate` for live logs).

**Q: Logs not rotating?**  
A: Make sure logrotate config file is in `/etc/logrotate.d/` and syntax is correct.

---

For advanced configs (multiple logs, size-based rotation, etc.), see the [logrotate man page](https://linux.die.net/man/8/logrotate).

---

*Last updated: November 2025*
