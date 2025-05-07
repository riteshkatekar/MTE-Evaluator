# 📊 MTE Evaluator

This is an automated system for evaluating Monthly Thinking Exercises (MTEs) submitted via email. It processes `.xlsx` submissions, uses AI to generate section-wise feedback, creates a detailed PDF report, and stores all materials in Google Drive student folders.

---

## 🚀 Features

- 📥 **Gmail API integration** to fetch unread MTE emails with `.xlsx` attachments  
- 🤖 **AI-powered section-wise evaluation** (GPT-based model via Groq API)  
- 🧾 **PDF feedback generation** with Unicode support and full student content  
- ☁️ **Google Drive integration**: automatic upload to student-specific folders  
- 📤 **Auto email report dispatch** to student and mentor  

---

## 🔐 Required Files (Manually Place in `app/` Folder)

These files are **excluded from version control** via `.gitignore`:

| File                 | Purpose                                         |
|----------------------|-------------------------------------------------|
| `credentials.json`   | Google Cloud OAuth 2.0 credentials              |
| `token.json`         | Generated after first successful OAuth login    |
| `system_config.json` | Mapping of student names/emails to Drive folders|

> ⚠️ **Do not share these files publicly.** They contain sensitive credentials.

---

## 📁 Folder Structure (Auto-Created)

These folders will be automatically created at runtime:

- `downloads/` → Incoming `.xlsx` MTE files from Gmail  
- `reports/` → Generated PDF feedback reports  

---

## ⚙️ How to Run

Ensure all required files are present in the `app/` directory, then run the app:

```bash
streamlit run main.py
```

---
##📬 Automated Email-Based Evaluation (Gmail + Google Drive)
- To activate the Google Workspace integration that automatically:

- Fetches .xlsx MTEs from Gmail

- Processes and evaluates each file

- Sends PDF reports to students and mentors

- Uploads files to Google Drive

```bash
python gmail_integration.py
```
