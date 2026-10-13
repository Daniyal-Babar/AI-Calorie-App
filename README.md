# NutriAgent — Chat-Only AI Calorie & Nutrition App

NutriAgent is a full-stack, autonomous nutrition coaching application designed around a **Chat-Only Architecture**. The frontend is a responsive, glassmorphic shell, while the backend runs an LLM agent with multi-turn tool calling directly interacting with nutrition models and services.

---

## 🌟 Key Features

1. **Autonomous Tool Calling**:
   - The LLM determines the tool to call: `analyze_meal`, `log_meal`, `edit_meal`, `delete_meal`, `get_daily_summary`, `get_weekly_report`, `set_calorie_goal`, `update_profile`, `generate_diet_plan`, `set_reminder`.
2. **Server-Side Security**:
   - `user_id` is never accepted as an argument from the LLM; the backend injects the authenticated user ID from the verified JWT.
3. **Safety & Destructive Action Confirmations**:
   - Operations like `delete_meal` trigger an interactive confirmation UI block before irreversible deletion.
4. **Deterministic In-Code Math**:
   - Mifflin-St Jeor BMR, TDEE, macronutrient splits, and daily calorie totals are computed in Python code, avoiding LLM math errors.
5. **Typed UI Response Blocks**:
   - Messages return structured blocks (`meal_card`, `daily_summary_card`, `diet_plan_card`, `actions`) rendered into dynamic cards.
6. **SSE Streaming**:
   - Real-time Server-Sent Events stream thinking statuses, tool call steps, and reply tokens.
7. **Smart Fallback**:
   - Runs out-of-the-box in local development with an offline heuristic agent, or with Google Gemini API when `GEMINI_API_KEY` is provided.

---

## 📂 Project Structure

```
ai-calorie-app/
├── backend/
│   ├── app/
│   │   ├── __init__.py              # create_app() factory
│   │   ├── config.py                # Environment configs & SQLite/Postgres fallback
│   │   ├── extensions.py            # db, migrate, jwt, cors
│   │   ├── models/                  # User, Meal, MealItem, DailyGoal, DietPlan, Conversation, Message, Reminder
│   │   ├── api/                     # Blueprints: auth, chat, uploads, health
│   │   ├── agent/                   # LLM Orchestrator, ContextBuilder, Guardrails, Tools registry
│   │   ├── services/                # MealService, CalorieService, DietService, NutritionLookup, UploadService
│   │   ├── schemas/                 # Pydantic schemas
│   │   ├── utils/                   # Rate limiter, errors, token counter
│   │   └── tasks/                   # Scheduler for chat reminder nudges
│   ├── migrations/                  # Alembic migrations
│   ├── tests/                       # Unit tests (tools, orchestrator, evals)
│   ├── requirements.txt
│   └── wsgi.py
│
├── frontend/
│   ├── src/
│   │   ├── api/                     # client.js, auth.js, chat.js, uploads.js
│   │   ├── context/                 # AuthContext
│   │   ├── hooks/                   # useAuth, useChat (SSE streaming)
│   │   ├── pages/                   # Login.jsx, Register.jsx, Chat.jsx
│   │   ├── components/              # MessageList, Composer, blocks (MealCard, DailySummaryCard, DietPlanCard)
│   │   └── main.jsx
│   └── package.json
│
├── docs/                            # Architecture and reference specs
├── docker-compose.yml               # Multi-container setup (Postgres, Backend, Frontend)
└── README.md
```

---

## 🚀 Getting Started

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python wsgi.py
```
*The backend starts at `http://localhost:5000` with automated database table creation.*

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*The frontend opens at `http://localhost:5173`.*

### 3. Docker Compose Setup
To launch the full PostgreSQL database, Flask backend, and React frontend in containers:
```bash
docker-compose up --build
```

---

## 🧪 Running Tests

The test suite validates tool functions, orchestration loops, and prompt-to-tool evals without requiring an external LLM connection:

```bash
cd backend
python -m pytest
```
