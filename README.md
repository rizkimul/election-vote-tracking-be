# Election Vote Tracking API

A robust FastAPI backend designed for managing election-related activities, participant tracking, and providing analytics for the Election Vote Tracking Dashboard.

## 🚀 Features

- **Authentication & Security:**
  - JWT-based authentication with Access and Refresh tokens.
  - Role-based access control (Admin/User).
  - Secure password hashing using Bcrypt.
- **Activity Management (Events):**
  - Create and track election activities/events.
  - Categorize events by type and location (Dapil, Kecamatan, Desa).
  - Target participant management.
- **Participant Tracking (Attendees):**
  - Record participants with NIK (National ID) or NIS (Student ID) validation.
  - Prevent duplicate entries per event.
  - Demographic tracking (Gender, Age, Occupation).
- **Analytics & Strategy:**
  - Real-time aggregation of attendance and demographic data.
  - Region-based participation analysis.
  - Prioritization logic for election strategy based on historical or attendance data.
- **Data Integration:**
  - Bulk import of participants via Excel files (.xlsx).
  - Export capabilities for reporting.

## 🛠 Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Database:** [SQLAlchemy](https://www.sqlalchemy.org/) (ORM) with [Alembic](https://alembic.sqlalchemy.org/) for migrations.
- **Data Processing:** [Pandas](https://pandas.pydata.org/), [Openpyxl](https://openpyxl.readthedocs.io/).
- **Validation:** [Pydantic](https://docs.pydantic.dev/).
- **Server:** [Uvicorn](https://www.uvicorn.org/).

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL or SQLite (configured via `.env`)

## ⚙️ Setup Instructions

1. **Clone the repository:**
   ```bash
   cd back-end/election-app
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Migrations:**
   ```bash
   alembic upgrade head
   ```

## 🏃 Running the API

Start the development server with:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`. You can access the interactive Swagger documentation at `http://localhost:8000/docs`.

## 🧪 Testing

Run tests using Pytest:
```bash
pytest
```
