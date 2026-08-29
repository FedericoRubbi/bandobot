# bandobot

A Telegram bot that scrapes Italian grant/incentive websites and notifies subscribed users of new announcements. Active scrapers: Cassa Depositi e Prestiti, Incentivi.gov.it, Lazio Innova, Obiettivo Europa, Qual Energia. (Gazzetta Ufficiale is a planned source, not yet implemented — see [scraping/gazzettaufficiale.py](scraping/gazzettaufficiale.py).)

## Requirements

- Python 3.13+
- A Telegram bot token (create one via [@BotFather](https://t.me/BotFather))

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd bandobot
   ```

2. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables by copying the example file and filling in your values:

   ```bash
   cp .env.example .env
   ```

   | Variable | Description |
   | --- | --- |
   | `TELEGRAM_BOT_TOKEN` | Token for your Telegram bot, obtained from BotFather |
   | `USERS_RECORDS_PATH` | Path to the JSON file storing registered users (defaults to `data/users/users.json`) |

## Usage

Run the bot:

```bash
python main.py
```

The bot will start polling Telegram and periodically scrape the configured sources for new announcements, notifying registered users.

## Windows executable (no Python required)

A prebuilt `bandobot.exe` is produced automatically by [.github/workflows/build-windows-exe.yml](.github/workflows/build-windows-exe.yml) for collaborators who don't want to install Python or clone the repo.

- Every push to a version tag (e.g. `v1.0.0`) publishes a `bandobot-windows.zip` on the repo's [Releases page](https://github.com/FedericoRubbi/bandobot/releases), containing `bandobot.exe`, `.env.example`, and an empty `data/` folder structure.
- You can also trigger a build manually from the Actions tab ("Build Windows exe" → "Run workflow"); this only uploads a temporary build artifact (expires after 90 days, requires a GitHub login to download).

To publish a new release build:

```bash
git tag v1.0.0
git push origin v1.0.0
```

For your collaborator:

1. Download and unzip `bandobot-windows.zip` from the [Releases page](https://github.com/FedericoRubbi/bandobot/releases).
2. Rename `.env.example` to `.env` (in the same folder as `bandobot.exe`) and fill in their own `TELEGRAM_BOT_TOKEN` (from their own BotFather bot).
3. Double-click `bandobot.exe` (or run it from a terminal to see logs).

The bot reads `.env` and stores `data/users` / `data/history` next to the executable itself, so it works regardless of which folder it's launched from — each collaborator can run their own copy with their own token and user list without touching the source code.
