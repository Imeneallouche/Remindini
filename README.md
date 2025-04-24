# Remindini – Intelligent Reminder & Alert System

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)  
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)  
[![Flask](https://img.shields.io/badge/Flask-2.0%2B-orange)](https://flask.palletsprojects.com/)  

---

## Table of Contents

1. [Project Overview](#project-overview)  
2. [Features](#features)  
3. [Architecture](#architecture)  
4. [Technology Stack](#technology-stack)  
5. [Prerequisites](#prerequisites)  
6. [Installation & Setup](#installation--setup)  
7. [Configuration](#configuration)  
8. [Usage](#usage)  
9. [Database Schema](#database-schema)  
10. [API Reference](#api-reference)  
11. [Development & Testing](#development--testing)  
12. [Roadmap](#roadmap)  
13. [Contributing](#contributing)  
14. [License](#license)  
15. [Contact & Acknowledgments](#contact--acknowledgments)  

---

## Project Overview

**Remindini** is an end-to-end reminder and alert system combining:
- **Google Calendar**-based SMS reminders  
- **IoT sensor monitoring** (temperature & humidity)  
- **Raspberry Pi** SMS gateway powered by Gammu & RaspiSMS  
- **Web UI** for users and administrators  

It delivers timely SMS notifications for scheduled events or when environmental thresholds are crossed.

---

## Features

- **User-driven reminders** via Google Calendar integration  
- **Sensor-based alerts** when temperature or humidity exceed user-defined thresholds  
- **Configurable delay & units** for reminder frequency  
- **SMS gateway** on Raspberry Pi with SIM800L/HAT  
- **Web dashboard**  
  - User portal: manage calendar integration, phone, thresholds  
  - Admin portal: monitor sent notifications, system health  
- **Edge platform** support for additional IoT workloads  

---

## Architecture

```mermaid
flowchart LR
  subgraph Client
    direction TB
    U[Users] --> RA[Remindini App]
    A[Admin] --> RI[RaspiSMS Interface]
    RA -->|REST API / WebSocket| CA[Control Application]
    RI -->|REST API / WebSocket| CA
  end

  subgraph RaspberryPi
    direction TB
    CA --> GAM[Gammu]
    GAM --> GC[Google Calendar API]
    GAM --> RS[RsapiSMS]
    CA --> EP[Edge Platform]
    CA --> DB[(PostgreSQL Database)]
    CA --> GSM[GSM Module - SIM800L]
    CA --> TM[Temperature Sensor - DHT22]
    CA --> HM[Humidity Sensor - DHT22]
  end
```

---

## Technology Stack

| Layer        | Technology                   |
|--------------|------------------------------|
| **Hardware** | Raspberry Pi 4, SIM800L HAT, DHT22 sensors |
| **Backend**  | Python 3.8+, Flask, SQLAlchemy, Gammu, RaspiSMS |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap |
| **Cloud/Edge** | Azure IoT Hub (optional), Custom Edge Platform |
| **Database** | PostgreSQL (or SQLite for dev) |

---

## Prerequisites

- **Hardware**  
  - Raspberry Pi 4 (with Raspbian)  
  - SIM800L GSM module or HAT  
  - DHT22 temperature & humidity sensor  

- **Software**  
  - Python 3.8+  
  - pip (or poetry)  
  - Git  
  - PostgreSQL (or SQLite)  
  - Google Cloud project with Calendar API enabled  

---

## Installation & Setup

1. **Clone the repo**  
   ```bash
   git clone https://github.com/yourorg/remindini.git
   cd remindini
   ```

2. **Create & activate virtualenv**  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**  
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. **Provision hardware on Raspberry Pi**  
   - Attach SIM800L to UART/GPIO, DHT22 to a data pin  
   - Install & configure Gammu & RaspiSMS  

---

## Configuration

Copy `.env.example` to `.env` and set:

```ini
# Flask
FLASK_APP=run.py
FLASK_ENV=production

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/remindini

# Google OAuth 2.0
GOOGLE_CLIENT_ID=…
GOOGLE_CLIENT_SECRET=…
GOOGLE_TOKEN_URI=https://oauth2.googleapis.com/token
GOOGLE_SCOPES="https://www.googleapis.com/auth/calendar.readonly"

# SMS / Gammu
GAMMU_CONFIG=/etc/gammu/config
PHONE_DEFAULT_REGION=US

# Sensor thresholds (defaults overridden per-user)
DEFAULT_TEMP_THRESHOLD=30.0
DEFAULT_HUM_THRESHOLD=90.0
```

---

## Usage

1. **Start the Flask server**  
   ```bash
   flask run --host=0.0.0.0 --port=5000
   ```

2. **On Raspberry Pi**  
   ```bash
   python control_app.py
   ```

3. **Access the UI**  
   - User portal: `http://<pi_ip>:5000/`
   - Admin portal: `http://<pi_ip>:5000/admin`

4. **Onboard your Google Calendar**  
   - Log in, grant calendar read permissions, store tokens.  

5. **Configure alerts**  
   - Enable/disable SMS, temp or humidity services  
   - Set thresholds & reminder delay  

---

## Database Schema

```mermaid
erDiagram
    USER {
        Integer id PK
        String username
        String email
        String phone_number
        Boolean sms_service_activated
        Boolean temperature_service_activate
        Boolean humidity_service_activate
        Float temperature_threshold
        Float humidity_threshold
        Integer reminder_delay
        String reminder_unit
        Integer token_id FK
    }
    TOKEN {
        Integer id PK
        String token
        String refresh_token
        String token_uri
        String client_id
        String client_secret
        String scopes
        String expiry
    }
    EVENT_NOTIFICATION {
        Integer id PK
        String event_id
        Integer user_id FK
    }

    USER ||--|| TOKEN           : "has_one"
    USER ||--o{ EVENT_NOTIFICATION : "has_many"
    TOKEN }|..|{ USER           : "belongs_to"
    EVENT_NOTIFICATION }o..|| USER : "belongs_to"

```

---

## API Reference

### Authentication
- **`GET /auth/google/login`**  
  Initiate OAuth2 flow  

- **`GET /auth/google/callback`**  
  Handle Google token exchange  

### User Endpoints
- **`GET /user/profile`**  
- **`POST /user/settings`**  
- **`POST /user/subscribe-events`**  

### Admin Endpoints
- **`GET /admin/notifications`**  
- **`GET /admin/system-status`**  

> Full OpenAPI spec in `docs/openapi.yaml`.

---

## Development & Testing

- **Code style**: [Black](https://github.com/psf/black), [Flake8](https://flake8.pycqa.org/)  
- **Run tests**:  
  ```bash
  pytest --cov=app
  ```
- **Pre-commit hooks**: configured in `.pre-commit-config.yaml`

---

## Roadmap

- [ ] Multi-calendar support  
- [ ] Two-factor authentication  
- [ ] WebSocket live-push for sensor readings  
- [ ] Docker & Kubernetes deployment recipes  
- [ ] Internationalization (i18n)

---

## Contributing

1. Fork the repo  
2. Create a feature branch (`git checkout -b feature/YourFeature`)  
3. Commit your changes (`git commit -m 'Add feature'`)  
4. Push to the branch (`git push origin feature/YourFeature`)  
5. Open a Pull Request  

Please read our [CONTRIBUTING.md](CONTRIBUTING.md) and follow the [Code of Conduct](CODE_OF_CONDUCT.md).

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## Contact & Acknowledgments

- **Imène Allouche** – [li_allouche@esi.dz](mailto:li_allouche@esi.dz)
- **Zineb GHODBANE** – [lz_ghodbane@esi.dz](mailto:lz_ghodbane@esi.dz)  
- **Amira HADDAD** – [la_haddad@esi.dz](mailto:la_haddad@esi.dz)  
- **Zineb DEBBIH** – [li_debbih@esi.dz](mailto:li_debbih@esi.dz)  
- **Nada KOUADRI** – [ln_kouadri@esi.dz](mailto:ln_kouadri@esi.dz)
- **Assala REBHI** – [la_rebhi@esi.dz](mailto:la_rebhi@esi.dz)  
- **Samia DEROUECHE** – [ls_deroueche@esi.dz](mailto:ls_deroueche@esi.dz)  

- Thanks to the **Gammu**, **RaspiSMS**, and **Flask** communities for their great tools and guidance.  
- Inspired by best practices in IoT & edge computing.
