# CSU-RFID-PYQT6 - Vehicle RFID Management System

A Python application for managing vehicle RFID data using PyQt6 and PostgreSQL.

## Features

- RFID vehicle data management
- User authentication system
- PostgreSQL database integration
- Windows startup configuration

## Prerequisites

- **PostgreSQL 12+**
- **Python 3.11+**

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/CSU-RFID-PYQT6.git
cd CSU-RFID-PYQT6
```

### 2. Setup Virtual Environment

```bash
python -m venv .venv
.venv/Scripts/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Configuration

#### 1. Create a PostgreSQL database

```bash
createdb mon
```

#### 2. Restore database schema

```bash
psql -d mon -f rfid_car_dump.sql
```

### 5. Environment Setup

#### 1. Copy the example

```bash
cp .env.example .env
```

#### 2. Update the `.env`

```bash
DB_HOST=localhost
DB_NAME=mon
DB_USERNAME=postgres
DB_PASSWORD=
```

## Running the app

1. Start PostgreSQL
2. Activate virtual environment using `.venv/Scripts/activate`
3. Launcg the app `python main.py`

## First-Time usage

Credentials

| username | password |
| -------- | -------- |
| admin    | admin    |
| viewer   | 1234     |

## Windows Startup Configuration

To launch the app automatically on system startup:

1. Press Win + R, type shell:startup, and press Enter

2. In the Startup folder:

   - Right-click → New → Shortcut

   - Browse to select main.py

   - Name the shortcut "CSU VeMon Startup"

## Troubleshooting

Database Connection Issues:

- Ensure PostgreSQL service is running
- Verify credentials in .env match your PostgreSQL setup

Missing Dependencies:

- Reinstall requirements: pip install -r requirements.txt

Permission Errors:

- Run PowerShell/CMD as Administrator for database operations
- Ensure dump file is in the project root directory
