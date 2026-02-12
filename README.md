# Supply Project - Windows 10 Setup Guide

## Prerequisites

- **Python 3.x** installed ([Download here](https://www.python.org/downloads/))
  - ⚠️ During installation, **check "Add Python to PATH"**
- **Git** installed ([Download here](https://git-scm.com/downloads))

---

## Setup Steps

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd <project-folder>
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

```bash
venv\Scripts\activate
```

You should see `(venv)` at the beginning of your terminal prompt.

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Apply Migrations

```bash
python manage.py migrate
```

### 6. Load the Database

```bash
python manage.py loaddata db.json
```

### 7. Run the Development Server

```bash
python manage.py runserver
```

The app will be available at **http://127.0.0.1:8000/**

---

## Troubleshooting

### "python" is not recognized

Use `python3` instead of `python`, or reinstall Python with the **"Add to PATH"** option checked.

### Virtual environment activation error (PowerShell)

If you get an execution policy error, run:

```bash
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Then try activating again.

### loaddata fails with content type errors

Try loading with exclusions:

```bash
python manage.py loaddata db.json --exclude contenttypes --exclude auth.permission
```

If that also fails, flush the database first:

```bash
python manage.py flush --no-input
python manage.py loaddata db.json
```

---

## Project Structure

```
├── db.json              # Database dump (for initial data load)
├── db.sqlite3           # SQLite database (auto-generated after migrate)
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
├── supply/              # Main app
└── supply_project/      # Django project settings
```

---

## Running as a Background Server (LAN Access)

This allows other devices on your local network to access the app.

### 1. Find Your Windows IP Address

```bash
ipconfig
```

Look for **IPv4 Address** under your active network adapter (e.g., `192.168.1.100`).

### 2. Allow the Host in Django Settings

Open `supply_project/settings.py` and update:

```python
ALLOWED_HOSTS = ['*']
```

Or for more security, specify your IP:

```python
ALLOWED_HOSTS = ['192.168.1.100', 'localhost', '127.0.0.1']
```

### 3. Allow Port Through Windows Firewall

Open **PowerShell as Administrator** and run:

```bash
netsh advfirewall firewall add rule name="Django Server" dir=in action=allow protocol=TCP localport=8000
```

### 4. Run the Server in the Background

#### Option A: Using `pythonw` (simplest)

```bash
pythonw manage.py runserver 0.0.0.0:8000
```

This runs the server with no terminal window. To stop it later:

```bash
taskkill /f /im pythonw.exe
```

#### Option B: Using `nssm` (runs as a Windows Service)

1. Download **NSSM** from [nssm.cc](https://nssm.cc/download)
2. Extract and open a terminal in the nssm folder
3. Install the service:

```bash
nssm install SupplyServer
```

4. In the GUI that opens, set:
   - **Path:** `C:\path\to\venv\Scripts\python.exe`
   - **Startup Directory:** `C:\path\to\project\`
   - **Arguments:** `manage.py runserver 0.0.0.0:8000`

5. Manage the service:

```bash
nssm start SupplyServer
nssm stop SupplyServer
nssm remove SupplyServer confirm
```

The service will **auto-start on boot** and run in the background.

#### Option C: Using `waitress` (production-grade WSGI server)

1. Install waitress:

```bash
pip install waitress
```

2. Run the server:

```bash
pythonw -m waitress --host=0.0.0.0 --port=8000 supply_project.wsgi:application
```

Or combine with **nssm** (Option B) for a production-ready background service.

### 5. Access from Other Devices

On any device connected to the same network, open a browser and go to:

```
http://192.168.1.100:8000
```

Replace `192.168.1.100` with your actual Windows IP address.

---

## Useful Commands

| Command | Description |
|---|---|
| `python manage.py runserver` | Start dev server |
| `python manage.py migrate` | Apply database migrations |
| `python manage.py createsuperuser` | Create an admin user |
| `python manage.py shell` | Open Django shell |
| `deactivate` | Exit virtual environment |