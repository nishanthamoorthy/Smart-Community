# 🌍 Smart Community Resource & Volunteer Allocation System

A full-stack web application for NGOs to centralize community issue data,
auto-prioritize urgent needs, and match volunteers efficiently.

---

## 🗂️ Project Structure

```
smart-community/
├── backend/
│   ├── app.py              ← Flask application (all APIs)
│   └── requirements.txt    ← Python dependencies
├── database/
│   └── schema.sql          ← MySQL schema + seed data
├── templates/
│   ├── index.html          ← Home page
│   ├── dashboard.html      ← NGO admin dashboard with charts
│   ├── add_issue.html      ← Report community issue (with map picker)
│   ├── volunteer.html      ← Volunteer register/login/tasks
│   └── map.html            ← Interactive issue map
└── static/
    ├── css/style.css       ← Main stylesheet
    └── js/main.js          ← Shared JS utilities + API helpers
```

---

## ⚙️ Prerequisites

- Python 3.8+
- MySQL 8.0+
- pip

---

## 🚀 Step-by-Step Setup

### Step 1: Clone or extract the project

```bash
cd smart-community
```

### Step 2: Set up MySQL database

Open MySQL and run the schema:

```bash
mysql -u root -p < database/schema.sql
```

Or copy-paste the contents of `database/schema.sql` into MySQL Workbench.

This creates the database, all tables, and adds sample seed data.

### Step 3: Install Python dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 4: Configure database credentials

Edit `backend/app.py` lines 22–29 (DB_CONFIG section):

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',          # ← your MySQL username
    'password': 'yourpassword',  # ← your MySQL password
    'database': 'smart_community',
    'autocommit': True
}
```

Or set environment variables instead:

```bash
export DB_USER=root
export DB_PASSWORD=yourpassword
```

### Step 5: Run the Flask server

```bash
# From inside the backend/ folder:
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

### Step 6: Open in browser

Navigate to: **http://localhost:5000**

---

## 📄 Pages

| URL | Description |
|-----|-------------|
| `/` | Home page with live stats |
| `/dashboard` | NGO admin dashboard with charts + issue table |
| `/add_issue` | Report a new community issue with map picker |
| `/map` | Interactive Leaflet map of all issues |
| `/volunteer` | Volunteer register/login/tasks portal |

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/add_issue` | Submit a new issue |
| GET | `/api/get_issues` | Get all issues (filterable) |
| POST | `/api/register_volunteer` | Register a new volunteer |
| POST | `/api/login_volunteer` | Volunteer login |
| POST | `/api/assign_volunteer` | Assign volunteer to issue |
| GET | `/api/match_volunteers/<id>` | Get smart-matched volunteers |
| GET | `/api/my_tasks` | Get tasks for logged-in volunteer |
| GET | `/api/stats` | Dashboard statistics |
| GET | `/api/get_volunteers` | List all volunteers |
| PATCH | `/api/update_issue/<id>` | Update issue status |

---

## ⚡ Smart Logic

### Auto-Priority
Issues are automatically marked **HIGH PRIORITY** when:
```
people_affected > 100  AND  severity = 'high'
```

### Volunteer Matching (Haversine + Skill)
Volunteers are ranked for each issue by a score:
- **+50 points** if their skill matches the issue category
- **+up to 30 points** based on geographic proximity (closer = more points)

---

## 🧪 Demo Credentials (Volunteer Login)

| Email | Password |
|-------|----------|
| priya@example.com | volunteer123 |
| suresh@example.com | volunteer123 |
| meena@example.com | volunteer123 |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python Flask |
| Database | MySQL |
| Frontend | HTML, CSS, Vanilla JavaScript |
| Charts | Chart.js |
| Maps | Leaflet.js + OpenStreetMap + CartoDB |
| Password Hashing | bcrypt |

---

## 🗃️ Database Tables

### `issues`
| Column | Type | Notes |
|--------|------|-------|
| id | INT | Auto increment PK |
| title | VARCHAR(255) | Issue title |
| description | TEXT | Details |
| location | VARCHAR(255) | Human-readable location |
| latitude | DECIMAL | For map |
| longitude | DECIMAL | For map |
| severity | ENUM | low/medium/high |
| people_affected | INT | Count |
| priority | ENUM | normal/high (auto-calculated) |
| status | ENUM | open/in_progress/resolved |
| category | VARCHAR | general/medical/disaster/etc |
| created_at | TIMESTAMP | Auto |

### `volunteers`
| Column | Type | Notes |
|--------|------|-------|
| id | INT | Auto increment PK |
| name | VARCHAR | Full name |
| email | VARCHAR | Unique |
| password_hash | VARCHAR | bcrypt hash |
| skill | ENUM | doctor/driver/teacher/etc |
| location | VARCHAR | City/area |
| latitude | DECIMAL | For proximity matching |
| longitude | DECIMAL | For proximity matching |
| is_available | BOOLEAN | Availability flag |

### `assignments`
| Column | Type | Notes |
|--------|------|-------|
| id | INT | Auto increment PK |
| issue_id | INT | FK → issues |
| volunteer_id | INT | FK → volunteers |
| assigned_at | TIMESTAMP | When assigned |
| status | ENUM | assigned/completed |

---

## 📝 Notes for Beginners

1. Flask's `render_template()` serves HTML files from the `templates/` folder
2. Static files (CSS, JS) are served from `static/`
3. The `API` object in `main.js` is a simple wrapper around `fetch()` for all backend calls
4. `bcrypt` is used to safely hash passwords — **never store plain-text passwords**
5. Leaflet.js uses **free** OpenStreetMap tiles — no API key needed
