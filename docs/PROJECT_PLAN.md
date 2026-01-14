# TRAINING Project: Handover & Overview

This document serves as the "brain" for any AI assistant (or human developer) taking over this project. It captures the current state, architecture, and core logic.

## 1. Project Vision
A robust trading platform simulation with a Django backend and a React frontend. The goal is to implement high-precision financial logic (8 decimal places) and a reliable service-oriented architecture.

## 2. Technical Stack
- **Backend**: Django 5.x
- **Frontend**: Vite + React
- **Database**: SQLite (Migrated from AWS RDS after access loss).
- **Communication**: REST API (Django Rest Framework).
- **Portability**: All logic is Python-based to support Windows and macOS.

## 3. Core Business Logic (Services)
We use a **Service-Oriented Architecture** to keep logic out of models/views:
- **`BalanceService`**: Handles atomic `deposit` and `withdraw` operations with row-level locking.
- **`TradingService`**: Implements **Net Position Logic**:
    - Calculates Average Price when increasing exposure.
    - Realizes PnL when reducing or closing exposure.
    - Handles "Flipping" (going from Long to Short in one trade).

## 4. Current State & Recovery
- **Database Status**: Healthy. Migrated to SQLite (`db.sqlite3`).
- **Superuser**: A fresh superuser has been created on the current machine.
- **Migration Ready**: Use `scripts/backup_db.py` and `scripts/restore_db.py` to move data.
- **Documentation**: 
    - [RECOVERY_GUIDE.md](file:///c:/Users/JoseParra/OneDrive%20-%20Red%20Acre%20Ltd/Desktop/git/TRAINING/docs/RECOVERY_GUIDE.md): Technical steps for migration.
    - `docs/PROJECT_PLAN.md`: This document.

## 5. Team & Collaboration
This project is a collaborative effort between **Jose Parra** and his team of **AI Agents**.
- **Source of Truth**: The GitHub repository is the ultimate source of truth for code and documentation.
- **Branch Strategy**: Currently working on `feature/frontend-scaffold`.

## 6. Pending / Future Goals
- [ ] Implement more complex commission profiles.
- [ ] Expand the React frontend for real-time trade monitoring.
- [ ] Integrate real-time price feeds.
- [ ] Perfect the "Full Migration" to macOS environment.
