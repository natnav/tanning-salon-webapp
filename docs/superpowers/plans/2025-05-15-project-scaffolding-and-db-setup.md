# Project Scaffolding & Database Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Setup basic FastAPI app and Database configuration.

**Architecture:** Basic FastAPI application with SQLAlchemy ORM using SQLite.

**Tech Stack:** FastAPI, SQLAlchemy, SQLite, pytest, httpx.

---

### Task 1: Setup Test Structure & Failing Sanity Test

**Files:**
- Create: `tests/test_main.py`
- Create: `app/__init__.py`

- [ ] **Step 1: Create directories**

Run: `mkdir -p app tests`

- [ ] **Step 2: Create empty __init__.py**

Run: `touch app/__init__.py`

- [ ] **Step 3: Write the failing sanity test**

```python
from fastapi.testclient import TestClient
import pytest

def test_read_main():
    from app.main import app
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Tanning Salon API"}
```

- [ ] **Step 4: Run test to verify it fails**

Run: `pytest tests/test_main.py`
Expected: FAIL (ModuleNotFoundError: No module named 'app.main')

---

### Task 2: Implement Basic FastAPI App

**Files:**
- Create: `app/main.py`

- [ ] **Step 1: Write minimal implementation**

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Tanning Salon API"}
```

- [ ] **Step 2: Run test to verify it passes**

Run: `pytest tests/test_main.py`
Expected: PASS

---

### Task 3: Setup Database Configuration

**Files:**
- Create: `app/database.py`

- [ ] **Step 1: Write database configuration**

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./tanning_salon.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

- [ ] **Step 2: Verify database file is created (optional/manual)**
- [ ] **Step 3: Run tests again to ensure no regressions**

Run: `pytest tests/test_main.py`
Expected: PASS
