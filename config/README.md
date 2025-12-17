# ⚙️ Configuration

This directory requires your Google Calendar authentication files.
These files are not included in the repository for security.

## 📥 Setup Instructions

Please place the following two files in this directory:

### 1. `credentials.json` (API Key)
* **What is it:** The OAuth Client ID from Google Cloud.
* **How to get it:**
    1.  Go to Google Cloud Console > APIs & Services > Credentials.
    2.  Create an **OAuth Client ID** (Application Type: Desktop App).
    3.  Download the JSON and save it here as `credentials.json`.

### 2. `token.json` (Session Token)
* **What is it:** Your active login session.
* **How to generate it:**
    1.  Run the helper script in the root folder:
        ```bash
        python generate_token.py
        ```
    2.  Login via the browser.
    3.  Move the generated `token.json` file into this folder.

---

### ✅ Directory Status
Once configured, your folder should look like this:
```text
/config
├── README.md
├── credentials.json
└── token.json
```