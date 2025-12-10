.PHONY: help install-backend install-frontend install run-backend run-frontend test-backend test-frontend clean

help:
	@echo "Text-to-SQL Evaluation System - Available Commands"
	@echo ""
	@echo "  make install           - Install all dependencies (backend + frontend)"
	@echo "  make install-backend   - Install backend dependencies"
	@echo "  make install-frontend  - Install frontend dependencies"
	@echo "  make run-backend       - Run backend development server"
	@echo "  make run-frontend      - Run frontend development server"
	@echo "  make test-backend      - Run backend tests"
	@echo "  make test-frontend     - Run frontend tests"
	@echo "  make clean             - Clean build artifacts and caches"
	@echo ""

install: install-backend install-frontend

install-backend:
	@echo "Installing backend dependencies..."
	cd backend && python3 -m venv venv && . venv/bin/activate && pip install -r requirements.txt

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

run-backend:
	@echo "Starting backend server..."
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	@echo "Starting frontend development server..."
	cd frontend && npm run dev

test-backend:
	@echo "Running backend tests..."
	cd backend && . venv/bin/activate && pytest

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm test

clean:
	@echo "Cleaning build artifacts..."
	rm -rf backend/__pycache__
	rm -rf backend/app/__pycache__
	rm -rf backend/.pytest_cache
	rm -rf backend/charts
	rm -rf backend/exports
	rm -rf frontend/dist
	rm -rf frontend/node_modules/.cache
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Clean complete!"
