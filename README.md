# MTE Evaluator

This is an automated system for evaluating Monthly Thinking Exercises (MTEs) submitted via email. It processes `.xlsx` files, generates PDF feedback, and stores everything on Google Drive.

## 🚀 Features

- Gmail API integration for email and attachment fetching.
- AI-based feedback generation (section-wise).
- PDF report generation with Unicode support.
- Google Drive API for student folder management and report uploads.

---

## 🔐 Required Files (Not Included in Repository)

Please manually add these **required files** in the `app/` folder:

| File | Purpose |
|------|---------|
| `credentials.json` | OAuth2 credentials from Google Cloud |
| `token.json` | Generated after first successful OAuth2 login |
| `system_config.json` | Student-to-folder mappings for Drive upload |

**These files are excluded via `.gitignore` for security.**

---

## 📁 Folder Structure (Auto-created if missing)

These folders will be created on runtime:

- `downloads/`: Incoming `.xlsx` files from Gmail
- `feedback_records/`: Feedback JSON for auditing
- `reports/`: Generated PDF reports

---

## ⚙️ Running the Project

Run the main script:

```bash
python main.py
