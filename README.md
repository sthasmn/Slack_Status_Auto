# 🔄 Slack Status Sync With Calendar

**Stop interrupting your deep work to update your status.**

This tool automatically syncs your Google Calendar to your Slack status in real-time. It acts as your silent digital assistant, letting your colleagues know exactly when you are busy, in a meeting, or out for lunch—without you ever touching Slack.

### ⚡️ Why use this at work?
* **Focus Protection:** Automatically shows "In a Meeting" or "Coding" so colleagues know not to disturb you.
* **Context Aware:** Uses smart keywords to pick the right icon (e.g., "Lunch" → 🍱, "Deep Work" → 🧠, "Commuting" → 🚋).
* **Privacy First:** If you mark a calendar event as "Private", this bot simply shows "Busy" 🔒 without revealing the details.
* **Set & Forget:** Runs on your office server or PC (Docker) and restarts automatically if the system reboots.

---

## 📋 What you need
To make this work, you need two keys:
1.  **Google Calendar Authorization:** To let the bot *read* your schedule.
2.  **A Simple Slack App:** To let the bot *write* your status.

Don't worry—you don't need to be a developer to set this up. Follow the guide below.

---

## 1️⃣ Part 1: Google Calendar Setup
*Goal: Get the `credentials.json` file.*

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project (e.g., `Slack-Status-Sync`).
3.  **Enable API:** Search for "Google Calendar API" and enable it.
4.  **OAuth Consent Screen (Important):**
    * Select **External**.
    * **Add Test User:** You must add **your own email address** to the "Test Users" list. (If you skip this, the login will fail later).
5.  **Create Credentials:**
    * Go to **Credentials** → **Create Credentials** → **OAuth Client ID**.
    * Select **Desktop App**.
    * Download the JSON file and rename it to `credentials.json`.

---

## 2️⃣ Part 2: Slack App Setup
*Goal: Get the User Token (`xoxp-...`).*

1.  Go to [Slack API Apps](https://api.slack.com/apps) and click **Create New App** -> **From Scratch**.
2.  Name it (e.g., "Status Bot") and pick your workspace.
3.  **Add Permissions:**
    * In the sidebar, click **OAuth & Permissions**.
    * Scroll down to **User Token Scopes** (NOT Bot Token Scopes).
    * Add these two permissions:
        * `users.profile:write` (To change your status)
        * `users.profile:read` (To check your current status)
4.  **Install:** Scroll up and click **Install to Workspace**.
5.  **Copy Token:** Copy the **User OAuth Token** that starts with `xoxp-...`.

---

## 3️⃣ Part 3: Installation & Run

### A. Authentication (One-time Setup)
*If your server has no screen (headless), run this step on your local PC/Mac first.*

1.  Install dependencies:
    ```bash
    pip install google-auth-oauthlib google-api-python-client
    ```
2.  Run the helper script included in this repo:
    ```bash
    python generate_token.py
    ```
3.  Login via the browser popup. This generates a `token.json` file.
4.  **Move** `credentials.json` and `token.json` to your server's `config/` folder.

### B. Docker Deployment
1.  Open `docker-compose.yml` and paste your Slack Token:
    ```yaml
    services:
      slack-bot:
        environment:
          - SLACK_TOKEN=xoxp-your-token-here...
    ```
2.  Start the bot:
    ```bash
    docker compose up -d --build
    ```
3.  Check logs:
    ```bash
    docker logs -f slack_calendar_bot
    ```

---

## 🧠 Smart Emoji Mapping
The bot is smart. It looks for keywords in your event title. You can customize this in `sync_bot.py`.

| Keyword in Calendar | Slack Icon |
| :--- | :--- |
| `meeting`, `mtg`, `会議` | 👥 (`:busts_in_silhouette:`) |
| `lunch`, `break` | 🍱 (`:bento:`) |
| `lecture`, `class` | 🎓 (`:mortar_board:`) |
| `experiment`, `lab`, `実験` | ⚗️ (`:alembic:`) |
| *No match* | 📅 (`:calendar:`) |

---

## 📄 License
Open source. Feel free to use and modify for your personal workflow.