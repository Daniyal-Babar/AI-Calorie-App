# NutriAgent: Chat-Only AI Calorie App Architecture

## 1. Overview
The **Chat-Only Architecture** transforms traditional complex form-heavy calorie tracking apps into an intuitive conversational agent. The frontend serves as a responsive, lightweight display shell, while the backend orchestrates an LLM agent with direct database tool-calling.

```
+-----------------------------------------------------------+
|                    Thin Frontend Shell                     |
|  (React + SSE Stream Receiver + Typed Blocks Renderer)    |
+-----------------------------+-----------------------------+
                              |
                     POST /api/chat (SSE)
                              v
+-----------------------------------------------------------+
|                      Flask Backend                        |
|                                                           |
|  +-----------------------------------------------------+  |
|  |                Agent Orchestrator                   |  |
|  |  1. ContextBuilder (Profile + Goals + Today Totals) |  |
|  |  2. Guardrails (Safety check, Scope, Disclaimers)   |  |
|  |  3. LLM Multi-Turn Loop (Max ~5 iterations)         |  |
|  |  4. Tool Registry & Server-Side Security            |  |
|  |  5. Response Block Formatter                        |  |
|  +-----------------------------------------------------+  |
|                             |                             |
|       +---------------------+---------------------+       |
|       v                     v                     v       |
|  [MealService]      [CalorieService]        [DietService] |
|       \                     |                     /       |
|        +--------------------+--------------------+        |
|                             v                             |
|                   PostgreSQL / SQLite                     |
+-----------------------------------------------------------+
```

## 2. Key Architecture Pillars

### 1. The LLM Never Touches SQL Directly
The LLM communicates exclusively via registered OpenAI Function Calling tools (`log_meal`, `get_daily_summary`, `set_calorie_goal`, etc.). Every parameter is validated through Pydantic schemas.

### 2. Server-Side User Injection
The LLM is NEVER allowed to specify `user_id` as a parameter. The backend orchestrator extracts `user_id` directly from the authenticated JWT token and binds it in Python. This completely prevents cross-tenant data leakage or prompt injection attacks.

### 3. Confirmation on Destructive Actions
Actions such as deleting a meal (`delete_meal`) or overwriting major profile data do not immediately delete records. Instead, they produce a `pending_confirmation` status and return an interactive UI action block to the frontend.

### 4. Deterministic In-Code Nutrition Math
All metabolic calculations (BMR Mifflin-St Jeor, TDEE, macronutrient distributions, deficit calculations) are computed deterministically in `calorie_service.py` rather than relying on LLM arithmetic.

### 5. Abstract UI via Typed Response Blocks
Instead of unstructured text blobs, the agent streams structured blocks:
- `text`: Natural language explanations
- `meal_card`: Interactive food & macro breakdown card
- `daily_summary_card`: Radial progress & consumed vs. target macro gauges
- `diet_plan_card`: Multi-meal structured regimen
- `actions`: Confirmation action buttons
