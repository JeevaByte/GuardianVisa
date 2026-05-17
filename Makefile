# GuardianVisa — Developer Makefile
# Usage: make <target>

# ANSI colour codes
BOLD   := \033[1m
RESET  := \033[0m
GREEN  := \033[0;32m
YELLOW := \033[0;33m
CYAN   := \033[0;36m
RED    := \033[0;31m

.DEFAULT_GOAL := help

.PHONY: help install seed validate dev-backend dev-frontend build-frontend \
        docker-up docker-down deploy logs-backend logs-frontend \
        setup-env check-env clean

# ─────────────────────────────────────────────────────────────────────────────
# Help
# ─────────────────────────────────────────────────────────────────────────────

help: ## Print all targets with descriptions
	@echo ""
	@echo "$(BOLD)$(CYAN)GuardianVisa — Developer Makefile$(RESET)"
	@echo "$(CYAN)────────────────────────────────────────────────────$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Setup
# ─────────────────────────────────────────────────────────────────────────────

setup-env: ## Copy backend/.env.example → backend/.env (fill in credentials)
	@if [ -f backend/.env ]; then \
		echo "$(YELLOW)⚠️  backend/.env already exists — skipping copy$(RESET)"; \
	else \
		cp backend/.env.example backend/.env; \
		echo "$(GREEN)✅ backend/.env created — fill in your credentials$(RESET)"; \
	fi

check-env: ## Verify all required env vars in backend/.env are set (not placeholders)
	@echo "$(CYAN)🔍 Checking backend/.env for placeholder values...$(RESET)"
	@if [ ! -f backend/.env ]; then \
		echo "$(RED)❌ backend/.env not found. Run: make setup-env$(RESET)"; exit 1; \
	fi
	@MISSING=0; \
	while IFS= read -r line; do \
		case "$$line" in \#*|"") continue ;; esac; \
		key=$$(echo "$$line" | cut -d'=' -f1); \
		val=$$(echo "$$line" | cut -d'=' -f2-); \
		case "$$val" in \
			*"your-"*|*"username"*|*"password"*|*"<"*|"") \
				echo "$(RED)  ❌ $$key is still a placeholder$(RESET)"; MISSING=1 ;; \
			*) echo "$(GREEN)  ✅ $$key$(RESET)" ;; \
		esac; \
	done < backend/.env; \
	if [ "$$MISSING" -eq 1 ]; then \
		echo "$(RED)$(BOLD)Some env vars are not configured. Edit backend/.env$(RESET)"; exit 1; \
	else \
		echo "$(GREEN)$(BOLD)All env vars look good!$(RESET)"; \
	fi

install: ## Install Python deps (backend) + Node deps (frontend)
	@echo "$(CYAN)📦 Installing Python dependencies...$(RESET)"
	pip install -r backend/requirements.txt
	@echo "$(CYAN)📦 Installing Node dependencies...$(RESET)"
	cd frontend && npm install
	@echo "$(GREEN)✅ All dependencies installed$(RESET)"

# ─────────────────────────────────────────────────────────────────────────────
# Data
# ─────────────────────────────────────────────────────────────────────────────

seed: ## Seed MongoDB with demo data (students, visa rules, scam patterns, resources)
	@echo "$(CYAN)🌱 Seeding MongoDB...$(RESET)"
	python data/seed_mongodb.py
	@echo "$(GREEN)✅ MongoDB seeded$(RESET)"

validate: ## Run full pre-flight validation (MongoDB + GCP connectivity)
	@echo "$(CYAN)🔍 Running system validation...$(RESET)"
	python scripts/validate_all.py

# ─────────────────────────────────────────────────────────────────────────────
# Local development
# ─────────────────────────────────────────────────────────────────────────────

dev-backend: ## Start FastAPI backend with hot-reload on port 8000
	@echo "$(CYAN)🚀 Starting backend on http://localhost:8000$(RESET)"
	cd backend && uvicorn main:app --reload --port 8000

dev-frontend: ## Start Vite dev server (React frontend) on port 5173
	@echo "$(CYAN)🚀 Starting frontend on http://localhost:5173$(RESET)"
	cd frontend && npm run dev

build-frontend: ## Build frontend for production (outputs to frontend/dist)
	@echo "$(CYAN)🔨 Building frontend...$(RESET)"
	cd frontend && npm run build
	@echo "$(GREEN)✅ Frontend built → frontend/dist$(RESET)"

# ─────────────────────────────────────────────────────────────────────────────
# Docker
# ─────────────────────────────────────────────────────────────────────────────

docker-up: ## Build and start all services with docker-compose
	@echo "$(CYAN)🐳 Starting services with Docker Compose...$(RESET)"
	docker-compose up --build

docker-down: ## Stop and remove all docker-compose services
	@echo "$(CYAN)🐳 Stopping Docker Compose services...$(RESET)"
	docker-compose down
	@echo "$(GREEN)✅ All services stopped$(RESET)"

# ─────────────────────────────────────────────────────────────────────────────
# Deployment
# ─────────────────────────────────────────────────────────────────────────────

deploy: ## Deploy to Google Cloud Run via Cloud Build
	@echo "$(CYAN)☁️  Submitting Cloud Build job...$(RESET)"
	gcloud builds submit . --config=deploy/cloudbuild.yaml
	@echo "$(GREEN)✅ Deployment submitted$(RESET)"

logs-backend: ## Stream backend logs from Cloud Run (us-central1)
	@echo "$(CYAN)📋 Fetching backend logs...$(RESET)"
	gcloud run logs read --service guardianvisa-backend --region us-central1

logs-frontend: ## Stream frontend logs from Cloud Run (us-central1)
	@echo "$(CYAN)📋 Fetching frontend logs...$(RESET)"
	gcloud run logs read --service guardianvisa-frontend --region us-central1

# ─────────────────────────────────────────────────────────────────────────────
# Cleanup
# ─────────────────────────────────────────────────────────────────────────────

clean: ## Remove build artefacts and caches
	@echo "$(CYAN)🧹 Cleaning build artefacts...$(RESET)"
	rm -rf frontend/dist frontend/node_modules backend/__pycache__
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Clean complete$(RESET)"
