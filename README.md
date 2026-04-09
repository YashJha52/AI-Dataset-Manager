# ⚡ AI Dataset Manager

> A full-stack, self-hosted web application for managing the complete lifecycle of AI/ML datasets — versioning, experiment tracking, model registry, and team-based access control.

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=flat-square&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479A1?style=flat-square&logo=mysql&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=flat-square&logo=bootstrap&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📋 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Database Design](#-database-design)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Usage Guide](#-usage-guide)
- [API Reference](#-api-reference)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)

---

## 🧠 About

AI Dataset Manager is a **DBMS-focused portfolio project** that solves a real problem in ML teams: the lack of structure around dataset management. As teams iterate on datasets and models, mistakes happen — files get silently overwritten, experiment results get disconnected from the data used to produce them, and there's no audit trail of who changed what.

This tool provides:
- **SHA-256 change detection** — rejects duplicate uploads automatically
- **Version-controlled datasets** — every change creates a new, traceable version
- **Experiment tracking** — links accuracy/loss metrics to the exact dataset version used
- **Role-based access** — Team Leads assign datasets to Developers through the portal
- **Full audit logging** — database-level trigger auto-logs every new version

It is designed to fill the gap between a basic filesystem and a full enterprise MLOps platform (like MLflow or DVC) — the **"just enough structure"** solution for academic teams, hackathons, and early-stage projects.

---

## ✨ Features

### 📦 Dataset Management
- Upload datasets (CSV, JSON, TSV, TXT)
- Automatic SHA-256 hash comparison — prevents duplicate version creation
- Searchable dataset list using MySQL **FULLTEXT** index
- CSV **data preview** (first 10 rows) directly in the browser

### 🔁 Version Control
- Automatic version increment on upload
- Visual **version timeline** grouped by dataset
- Full change history with user attribution and timestamps
- Manual change log entries for documenting transformations

### 🧪 Experiment Tracking
- Log accuracy and loss per (model, dataset version) pair
- **Chart.js** visualizations:
  - 📈 Accuracy & Loss over time (line chart)
  - 🏆 Model comparison by average accuracy (bar chart)
- Colour-coded accuracy indicators (green ≥ 90%, yellow ≥ 70%, red < 70%)

### 🤖 Model Registry
- Register named models with algorithm type (e.g. CNN, RandomForest, Transformer)
- Models are reused across experiments for consistent tracking

### 👥 Role-Based Access Control
| Role | Capabilities |
|---|---|
| **Team Lead** 🔑 | Create datasets · Assign datasets to Developers · View all data · Delete datasets |
| **Developer** 💻 | Access only assigned datasets · Upload new versions · Log changes · Preview data |

### 📊 Live Dashboard
- Real-time KPI counters — total datasets, versions, experiments, models, users
- Average experiment accuracy displayed as a badge
- Animated count-up on load

### 🗄️ Advanced DBMS Features
| Feature | Implementation |
|---|---|
| **Indexes** | 7 indexes on all FK columns to eliminate full table scans |
| **VIEWs** | `vw_dataset_summary`, `vw_best_experiments`, `vw_developer_assignments` |
| **TRIGGER** | `trg_after_version_insert` — auto-logs every new version at DB level |
| **FULLTEXT** | Native MySQL FULLTEXT index on dataset name + description |
| **Stored Procedure** | `GetDatasetExperiments(dataset_id)` — fetches experiment history per dataset |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3, Flask, Flask-CORS |
| **Database** | MySQL 8.0+ |
| **ORM / Driver** | mysql-connector-python (raw SQL — intentionally, to demonstrate DBMS concepts) |
| **Frontend** | HTML5, Vanilla CSS, Vanilla JavaScript |
| **UI Framework** | Bootstrap 5.3 |
| **Charts** | Chart.js 4.4 |
| **Fonts** | Google Fonts — Inter |
| **File Hashing** | Python `hashlib` (SHA-256) |
| **Config** | `python-dotenv` (`.env` file) |

> **Note:** Raw SQL is used intentionally (no ORM like SQLAlchemy) to demonstrate DBMS concepts including joins, views, triggers, stored procedures, and indexes.

---

## 🗄️ Database Design

### Entity-Relationship Overview

```
Users (user_id, name, email, role)
  │
  ├──< Datasets (dataset_id, dataset_name, description, created_by→Users)
  │         │
  │         ├──< Dataset_Versions (version_id, dataset_id, version_number, storage_path)
  │         │         │
  │         │         ├──< Dataset_Changes_Log (change_id, version_id, changed_by→Users, description)
  │         │         │
  │         │         └──< Experiments (experiment_id, model_id→Models, version_id, accuracy, loss)
  │         │
  │         └──< Dataset_Assignments (assignment_id, dataset_id, assigned_to→Users, assigned_by→Users)
  │
  └──< Models (model_id, model_name, algorithm)
```

### Views

```sql
-- Aggregate dataset stats (version count, experiment count, best accuracy, assignee count)
SELECT * FROM vw_dataset_summary;

-- Best experiments enriched with dataset and model info
SELECT * FROM vw_best_experiments;

-- Developer assignment view — who is assigned what, by whom
SELECT * FROM vw_developer_assignments;
```

### Stored Procedure

```sql
-- Get all experiments for a specific dataset
CALL GetDatasetExperiments(1);
```

---

## 📁 Project Structure

```
AI-Dataset-Manager/
│
├── backend/
│   ├── app.py              # Flask entry point, page routes, /stats endpoint
│   ├── db.py               # MySQL connection factory (uses .env)
│   ├── users.py            # User registration, role management
│   ├── datasets.py         # Dataset CRUD, versioning, assignment, search, preview
│   ├── experiments.py      # Experiment logging and analytics
│   ├── versions.py         # Version management
│   └── models.py           # Model registry
│
├── database/
│   ├── schema.sql          # Full DB schema (tables, indexes, views, trigger, SP)
│   └── queries.sql         # Sample analytical queries
│
├── frontend/
│   ├── dashboard.html      # Live KPI dashboard
│   ├── datasets.html       # Role-aware dataset management
│   ├── experiments.html    # Experiment logging + Chart.js analytics
│   ├── versions.html       # Visual version timeline
│   ├── models.html         # Model registry
│   └── login.html          # User registration with role selection
│
├── uploads/                # Dataset files stored here (git-ignored)
├── .env                    # Database credentials (git-ignored)
├── requirements.txt        # Python dependencies
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- pip

### 1. Clone the repository

```bash
git clone https://github.com/YashJha52/AI-Dataset-Manager.git
cd AI-Dataset-Manager
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=ai_dataset_manager
```

### 4. Set up the database

```bash
mysql -u root -p < database/schema.sql
```

### 5. Run the application

```bash
cd backend
python app.py
```

The server starts at **http://localhost:5000**

---

## 📖 Usage Guide

### First Time Setup

1. **Go to** `http://localhost:5000/login.html`
2. **Register a Team Lead** — select the 🔑 **Team Lead** role, enter name + email
3. **Save your User ID** — displayed after registration (e.g. `ID: 1`)
4. **Register Developers** — repeat for each team member using the 💻 **Developer** role

### Team Lead Workflow

1. Open **Datasets** → enter your User ID → click **Load My View**
2. Upload a dataset (CSV/JSON) using the **Create New Dataset** form
3. Click **🔑 Assign** on any dataset → select a developer → confirm
4. Repeat assignment for other datasets/developers as needed
5. Use **📖 History** to audit all changes across any dataset
6. Check the **Dashboard** for live KPI stats

### Developer Workflow

1. Open **Datasets** → enter your User ID → click **Load My View**
2. You see only the datasets your Team Lead has assigned to you
3. Click **⬆ New Version** to upload an updated file (SHA-256 checks for changes)
4. Click **✏️ Manual Log** to document what you changed (e.g. "Removed null rows")
5. Click **👁 Preview** to view the first 10 rows of a CSV dataset
6. After training a model, go to **Experiments** and log the results

### Logging Experiments

1. Go to **Experiments** page
2. Enter **Model ID** (from the Models page), **Version ID**, **Accuracy**, **Loss**
3. Submit → results appear in the table and both charts update live

---

## 🔌 API Reference

### Users
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/users/register` | Register a new user with role |
| `GET` | `/users/` | List all users |
| `GET` | `/users/<id>` | Get user info and role |

### Datasets
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/datasets/create` | Upload and create a new dataset |
| `GET` | `/datasets/` | List all datasets (lead view) |
| `GET` | `/datasets/my/<user_id>` | List datasets assigned to a developer |
| `GET` | `/datasets/search?q=` | FULLTEXT search across datasets |
| `GET` | `/datasets/preview/<id>` | First 10 rows of latest CSV version |
| `POST` | `/datasets/upload_version/<id>` | Upload new version (SHA-256 checked) |
| `POST` | `/datasets/assign` | Assign dataset to a developer |
| `DELETE` | `/datasets/unassign/<id>` | Remove an assignment |
| `GET` | `/datasets/assignments/<id>` | List developers assigned to a dataset |
| `POST` | `/datasets/log_change` | Manually log a change description |
| `GET` | `/datasets/history/<id>` | Get full change history for a dataset |
| `DELETE` | `/datasets/delete/<id>` | Delete dataset + all versions + files |

### Experiments
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/experiments/run` | Log a new experiment result |
| `GET` | `/experiments/` | List all experiments (enriched with model/dataset names) |
| `GET` | `/experiments/analytics` | Structured data for Chart.js (over-time + model comparison) |

### Models
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/models/create` | Register a new model |
| `GET` | `/models/` | List all models |

### Versions
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/versions/create` | Manually create a version entry |
| `GET` | `/versions/` | List all versions |

### Stats
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/stats` | Dashboard aggregate counts (datasets, versions, models, users, avg accuracy) |

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">
  Built with ❤️ as a DBMS portfolio project · <a href="https://github.com/YashJha52">@YashJha52</a>
</div>
