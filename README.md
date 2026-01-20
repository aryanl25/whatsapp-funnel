fastapi_server/{__init__.py,enums.py,models.py,schemas.py,security.py,database.py,dependencies.py,main.py, }
fastapi_server/routes/{__init__.py,auth.py, all other routes}
fastapi_server/services/extractor/{__init__.py} => for extracting information from each message, context handling
fastapi_server/services/decision_engine/{__init__.py} => for making a decision based on various rules (preset or dynamic)
fastapi_server/services/executor/{__init__.py} => for handling CTAs
fastapi_server/services/llm/{__init__.py} => llm api call
fastapi_server/services/whatsapp/{__init__.py} => only sending messages api





Pages
  - Login/Signup ( Organization and users )
    - auth/login -> only user login with roles
    - auth/signup -> includes both org and user signup
    - auth/logout
    - RUD orgs (no create - already created)
    - CRUD roles
    - CRUD users
  
  - Onboarding ( self business details, Agent details,  API setup(important) )
    - CRUD business-details (What business is this)
    - CRUD agent-details (How agent should behave)
    - API setup (for whatsapp phone number)
    - CRUD CTAs

  - Analytics/Dashboard ( general statistics )
    - general statistics
  - Settings ( general settings )
  - Leads (list of all people who have communicated until now)
    - CRUD leads
  - Action Center ( HITL )
    - R conversations
    - CRU messages
  - Inbox (Live conversations only)
    - RD conversations
    - R messages


Endpoints
auth/login
auth/signup
auth/logout

onboarding/business-details
onboarding/customer-details
onboarding/agent-details
onboarding/setup (for whatsapp phone number)

analytics/

settings/

leads/
leads/:id
leads/:id/messages

actions/
actions/:id

conversations/
conversations/:id

messages/
messages/:id















MASTER SPEC v2.1 - COMPLETE PRODUCTION-READY
WhatsApp Sales Agent + CRM (MVP → Production)

TABLE OF CONTENTS
Product Objective & Architecture
Auth & Org Setup
Onboarding Flow (with Pre-Run Config Generation)
WhatsApp Technical Details (Webhooks, Idempotency, Attribution)
WhatsApp Pricing & Policy (2024-2025)
Enums (Exhaustive)
Memory System (Token-Safe, Auto-Retrieval)
Staleness System (Anti-Spam)
Slot Confidence & Validation
CTA State Machine
Sentiment Timeline
Dynamic Message Budget
Multi-Language Support
Retrieval Quality Scoring
Policy Guardrails (Code-Enforced)
HTL Pipeline (Complete)
Follow-Up Logic (Inside & Outside 24h)
Escalation & Handoff
A/B Testing Framework
Config Versioning
Knowledge Staleness Detection
Reliability (Retries, Failsafe)
Cost Tracking
Data Deletion
Performance Budgets
Admin UI
Database Schema (Complete)
Backend Folder Structure
Frontend Folder Structure
Tech Stack & Deployment
MCP Tools (Scaffolded)
MVP Completion Criteria

1) PRODUCT OBJECTIVE & ARCHITECTURE
Goal: WhatsApp-first sales automation platform that qualifies, nurtures, closes, or escalates leads automatically.
Core Principles:
DB is source of truth
Small stable prompts + deep structured memory
HTL decides, Executor acts
Policy enforced in code, not LLM
24/7 operation (no business hours)
Tech Stack:
Backend: Python 3.11+, FastAPI, PostgreSQL, Redis, RQ
Frontend: Next.js, TypeScript, TailwindCSS, shadcn/ui
AI: LLM for HTL planning, extraction, summarization, critic
Deployment: API (Render/Fly), Web (Vercel), DB (Neon/Supabase), Redis (Upstash)

2) AUTH & ORG SETUP
MVP: Single org, single user DB Design: All tables include org_id for future multi-tenant
CREATE TABLE orgs (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE users (
  id UUID PRIMARY KEY,
  org_id UUID REFERENCES orgs(id),
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

Login: email + password → JWT tokens

3) ONBOARDING FLOW
User fills detailed questionnaire after registration. Required before agent can run.
Questionnaire Sections:
A. Business Basics
Name, industry, city, working hours, timezone
Website URL (mandatory), support email/phone
B. Offer Details
Products/services, pricing structure, USP, delivery timeline, refund policy
C. Target Customer (ICP)
Ideal customer description, disqualifiers, common use cases
D. Sales Process Preferences
Primary CTAs (ordered): BOOK_CALL, PAYMENT, APP_DOWNLOAD, SEND_DOCS, VISIT_WEBSITE, FILL_FORM
Budget qualification timing (early/mid/late/never)
Hot lead definition
Escalation triggers
E. FAQ Upload (Required)
User uploads faq.txt with Q&A pairs
System parses and stores in knowledge_docs
F. Policy Guardrails
Forbidden claims, required disclaimers, language restrictions, custom rules
G. Tone & Personality
Language (English/Hinglish/Hindi), honorifics, message length (5-25 words)
Questions per message (1 max), emoji policy (never/sparingly/frequent)
Formality (formal/professional/casual), persuasion level (soft/moderate/firm)
Website Auto-Scan
After URL provided, system fetches: homepage, pricing, about, FAQ, contact, terms/refund Stores chunks in knowledge_docs with source URLs
Pre-Run Config Generation
System generates and stores in business_profiles table:
1. BusinessConfig JSON (compact facts)
{
  "business_name": "JustStock Academy",
  "offer_summary": "Live trading courses, 3-tier pricing",
  "pricing_summary": "₹2999/₹5999/₹9999",
  "primary_ctas": ["APP_DOWNLOAD", "BOOK_CALL", "PAYMENT"],
  "disqualifiers": ["under 18", "outside India", "no capital"],
  "working_hours": "9 AM-9 PM IST Mon-Sat",
  "contact_links": {"app_url": "...", "website_url": "...", "booking_url": "..."},
  "timezone": "Asia/Kolkata"
}

2. SalesRules JSON (methodology)
{
  "qualification_checklist": {
    "experience_level": "required",
    "interest_category": "required",
    "goal": "required",
    "app_download_status": "required",
    "budget": "ask_late"
  },
  "objection_playbook": {
    "no_time": "Offer weekend batch, recorded sessions",
    "too_expensive": "Break down per-day cost, mention EMI"
  },
  "cta_sequencing": {"first": "APP_DOWNLOAD", "fallback": "BOOK_CALL"},
  "escalation_triggers": ["payment_failure", "angry_sentiment", "complex_question_3x"]
}

3. ToneProfile JSON (style rules)
{
  "language": "hi-en",
  "message_length_max_words": 15,
  "questions_per_message": 1,
  "honorifics": true,
  "emoji_policy": "never",
  "formality": "professional",
  "persuasion_level": "moderate",
  "examples": ["Namaste sir! App download kar liya?", "Demo class book karein?"]
}

4. Guardrails JSON (system + business rules)
{
  "system_guardrails": [
    "Never claim to be human",
    "Respect opt-out immediately",
    "No spam if user unresponsive >72h"
  ],
  "business_guardrails": [
    "Never guarantee trading profits",
    "Always mention risk disclaimer"
  ],
  "forbidden_phrases": ["guaranteed returns", "risk-free"],
  "required_disclaimers": ["Trading involves risk. Past performance ≠ future results."]
}

5. ScriptLibrary (indexed micro-templates)
{
  "openers": {"new_lead": "Hi! Interest in trading courses dekha. Help kar sakta hun!"},
  "qualification": {"experience_check": "Pehle trading ki hai?"},
  "objection_handlers": {"no_time": "Weekend batches + recorded sessions available!"},
  "cta_scripts": {"app_download": "App download: [LINK]"},
  "exits": {"graceful": "No problem! Jab ready ho, message karna."}
}

All configs editable in Admin UI with version control.

4) WHATSAPP TECHNICAL DETAILS
4.1 Webhook Handling (MANDATORY FAST RESPONSE)
Rule: Return 200 OK within 100ms to avoid retries.
@app.post("/webhooks/whatsapp")
async def webhook(payload: dict):
    # 1. Verify signature
    if not verify_signature(payload): return 401
    
    # 2. Parse event
    event = parse_webhook(payload)  # Extract: provider_message_id, from_number, text, etc.
    
    # 3. Store message (idempotency check via unique constraint)
    try:
        message = await store_message(event)
    except IntegrityError:  # Duplicate provider_message_id
        return {"status": "ok"}
    
    # 4. Enqueue job
    await enqueue_job("PROCESS_INBOUND_MESSAGE", conversation_id, message_id)
    
    # 5. Return 200 immediately
    return {"status": "ok"}

4.2 Idempotency
ALTER TABLE messages ADD CONSTRAINT unique_provider_msg_id 
  UNIQUE (provider_message_id);

4.3 Conversation Creation
First message from unknown number:
conversation = {
  "org_id": org_id,
  "channel": "whatsapp",
  "contact_phone": from_number,
  "lead_source": detect_source(metadata),  # See 4.4
  "status": "NEW",
  "stage": "NEW",
  "opted_out": False,
  "service_window_until": now + 24h,
  "nudge_count_window": 0,
  "last_user_message_at": now
}

4.4 Lead Attribution
Enum:
class LeadSource(Enum):
    ORGANIC_INBOUND = "organic_inbound"
    CLICK_TO_CHAT_AD = "click_to_chat_ad"
    WEBSITE_WIDGET = "website_widget"
    FORM_TO_WHATSAPP = "form_to_whatsapp"
    REFERRAL_LINK = "referral_link"
    QR_CODE = "qr_code"
    UNKNOWN = "unknown"

Store campaign metadata in conversations.campaign_metadata:
{
  "campaign_id": "SUMMER_2024",
  "ad_id": "123456",
  "utm_source": "facebook",
  "utm_campaign": "trading_jan",
  "referrer_url": "https://..."
}


5) WHATSAPP PRICING & POLICY (2024-2025)
5.1 Conversation Categories
Service (User-Initiated): FREE, no limits, 24h window
Utility Templates (Business-Initiated):
FREE within 24h window (as of July 2025)
CHARGED outside window (~₹0.40-₹1.00)
Use for: reminders, confirmations, updates
Marketing Templates: CHARGED (~₹0.50-₹1.50), max 2 per 24h without reply
Authentication Templates: CHARGED (~₹0.30-₹0.80), use for OTP/verification
5.2 Critical Rules
Template Pre-Approval: Submit to Meta, wait 12-48h
Quality Ratings: Low-quality templates get throttled
Opt-In Required: For marketing templates
Rate Limits: Tier-based (start: 1000 msgs/day)
5.3 Cost Optimization Strategy
Inside 24h: All FREE (service conversations)
- HTL responses, follow-ups, CTAs

Outside 24h: Use UTILITY templates (cheaper)
- Avoid MARKETING unless high-value lead

Goal: Keep conversation alive within 24h to stay free

5.4 Template Management
CREATE TABLE templates (
  id UUID PRIMARY KEY,
  org_id UUID,
  name TEXT,
  provider_template_id TEXT,
  category TEXT,  -- 'utility' / 'marketing' / 'authentication'
  language TEXT,
  body_preview TEXT,
  variables JSONB,
  approval_status TEXT,  -- 'pending' / 'approved' / 'rejected'
  quality_rating TEXT,
  created_at TIMESTAMP
);


6) ENUMS (EXHAUSTIVE)
class MessageType(Enum):
    TEXT, VOICE, IMAGE, DOCUMENT, VIDEO, TEMPLATE, BUTTON_REPLY, LIST_REPLY, SYSTEM

class ReasoningCode(Enum):
    INITIAL_GREETING, QUALIFICATION_QUESTION, DISCOVERY
    VALUE_PROPOSITION, OBJECTION_HANDLING, CTA_PUSH, PRICING_DISCUSSION
    SOFT_NUDGE, VALUE_ADD, SOCIAL_PROOF
    CLARIFICATION_REQUEST, CONFIRMATION
    STAY_SILENT, SCHEDULE_FOLLOWUP, EXIT_GRACEFUL, NEEDS_HUMAN

class CTAType(Enum):
    BOOK_CALL, PAYMENT, APP_DOWNLOAD, SEND_DOCS, VISIT_WEBSITE, FILL_FORM, SCHEDULE_DEMO, JOIN_WEBINAR

class LeadStatus(Enum):
    NEW, QUALIFYING, QUALIFIED, ENGAGED, HOT, WON, LOST, DROPPED, NEEDS_HUMAN, OPTED_OUT

class ConversationStage(Enum):
    NEW, INITIAL_CONTACT, DISCOVERY, QUALIFICATION, OBJECTION_HANDLING, 
    CTA_OFFERED, CTA_IN_PROGRESS, NEGOTIATION, CLOSED_WON, CLOSED_LOST, HUMAN_TAKEOVER, ARCHIVED

class StaleState(Enum):
    ACTIVE (<6h), COOLING (6-24h), COLD (24-72h), ARCHIVED (>72h)

class CTAState(Enum):
    NOT_OFFERED, OFFERED_ONCE, OFFERED_TWICE, CLICKED, COMPLETED, DECLINED

class EscalationPriority(Enum):
    CRITICAL, HIGH, MEDIUM, LOW

class Sentiment(Enum):
    VERY_POSITIVE, POSITIVE, NEUTRAL, FRUSTRATED, ANGRY


7) MEMORY SYSTEM
7.1 Memory Budget (Token Management)
MEMORY_BUDGET = {
    "stable_context": 500,    # BusinessConfig + ToneProfile + SalesRules + Guardrails
    "recent_messages": 800,   # Last 8-12 turns
    "summary": 250,           # Rolling summary
    "slots": 200,             # Extracted facts + commitments
    "retrieved": 300,         # Scroll-up snippets (if triggered)
    "knowledge": 300,         # FAQ/website (if needed)
    "total_max": 2500         # Hard ceiling
}

Truncation order: recent_messages → retrieved → knowledge (never truncate summary/slots)
7.2 Full Transcript
All messages stored forever in messages table (unless user requests deletion).
7.3 Structured Memory (conversation_state table)
Rolling Summary (100-250 tokens):
"User Rajesh (27, Mumbai) wants trading course. Has ₹10k capital. 
Main objection: no time. Interested in weekend batch. Asked about EMI.
Promised to check with family by Friday. Next: Follow up Friday evening with EMI details."

Slots (with confidence + source):
{
  "name": {"value": "Rajesh", "confidence": 0.95, "source_msg_id": 123},
  "budget": {"value": 10000, "confidence": 0.60, "source_msg_id": 128},
  "email": {"value": "r@example.com", "confidence": 0.85, "source_msg_id": 130}
}

Commitments:
{
  "user": [{"what": "Check with family", "due_time": "2024-01-12T18:00Z", "confidence": 0.8}],
  "agent": [{"what": "Send EMI details", "due_time": "2024-01-12T18:00Z"}]
}

Sentiment History:
[
  {"turn": 1, "sentiment": "neutral", "confidence": 0.8, "timestamp": "..."},
  {"turn": 3, "sentiment": "interested", "confidence": 0.9, "timestamp": "..."}
]

CTA States:
{
  "APP_DOWNLOAD": {
    "state": "OFFERED_ONCE",
    "first_offered_at": "...",
    "clicked": false,
    "completed": false
  }
}

Staleness State: "ACTIVE" (computed from last_user_message_at)
Response Rate:
{
  "total_bot_messages": 8,
  "total_user_replies": 5,
  "rate": 0.625,
  "avg_reply_time_seconds": 3600
}

7.4 Automatic Retrieval ("Scroll Up")
Triggers (automatic):
User references past context
Slot missing but required
Contradiction detected
HTL planner low confidence
Critic flags missing context
User asks factual question
Method:
def retrieve_with_scoring(query, conversation_id):
    candidates = semantic_search(query, conversation_id, top_k=10)
    relevant = [c for c in candidates if c.score > 0.7]
    scored = [(m, m.score*0.7 + recency_score(m)*0.3) for m in relevant]
    return sorted(scored, reverse=True)[:3]


8) STALENESS SYSTEM
States:
ACTIVE (<6h): Normal engagement, follow-ups allowed
COOLING (6-24h): Softer nudges only, value-add messages, max 1-2 msgs
COLD (24-72h): Templates only, minimal outreach
ARCHIVED (>72h): NO proactive outreach, only respond if user returns
Purpose: Prevents spam and saves cost.

9) SLOT CONFIDENCE & VALIDATION
Confidence Levels:
0.8+: Explicitly stated → High confidence
0.6-0.8: Implied → Medium confidence
<0.6: Guessed → Low confidence
HTL Rules:
if slot["confidence"] < 0.7 and major_cta:
    # Re-confirm before CTA
    message = f"Just to confirm, budget around ₹{slot['value']}?"

Overwriting:
if existing["confidence"] > 0.8 and new["confidence"] < 0.7:
    # Keep existing, ignore new


10) CTA STATE MACHINE
States: NOT_OFFERED → OFFERED_ONCE → OFFERED_TWICE / CLICKED / DECLINED / COMPLETED
Rules:
OFFERED_TWICE: Stop offering same CTA, try different approach
CLICKED: Wait for completion, don't spam
COMPLETED: Success, no need to offer again
DECLINED: User said no, switch strategy

11) SENTIMENT TIMELINE
Extract sentiment after each user message (VERY_POSITIVE, POSITIVE, NEUTRAL, FRUSTRATED, ANGRY).
Trend Analysis:
def analyze_trend(history):
    # Returns -1.0 (declining) to +1.0 (improving)
    # Use last 3 turns, compute slope

HTL Response:
Declining trend → Apologize, simplify, clarify
Angry → Escalate immediately
Improving → Good time for CTA

12) DYNAMIC MESSAGE BUDGET
def calculate_budget(conversation):
    base = 5
    if slots["budget"]["value"] > 10000: base += 2
    if response_rate < 0.3: base -= 2
    if sentiment_trend < 0: base -= 1
    return max(1, base)

Purpose: Invest in hot leads, reduce waste on cold leads.

13) MULTI-LANGUAGE SUPPORT
Detect language on first message, store in slots:
{"language_preference": {"value": "hi-en", "confidence": 0.9}}

Load language-specific scripts from ScriptLibrary.
HTL generates response in detected language.

14) RETRIEVAL QUALITY SCORING
Semantic search → filter (score > 0.7) → rerank (70% relevance + 30% recency) → top 3

15) POLICY GUARDRAILS (CODE-ENFORCED)
Module: policy_guardrails
Rules (non-overridable by LLM):
24h window enforcement (outside = templates only)
Opt-out enforcement (STOP detected → no more messages)
Message rate limits (dynamic budget cap)
Human takeover lock (status = NEEDS_HUMAN → bot stops)
Staleness cap (ARCHIVED → no outreach)
Idempotency (duplicate webhooks ignored)

16) HTL PIPELINE (COMPLETE)
16.1 HTL Function
HTL.think(compiled_context) -> DecisionJSON

16.2 Internal Stages
Planner: Decide stage, goal, should_send, message intent, retrieval trigger
(Optional) Retrieval: If triggered, fetch relevant past messages
Writer: Generate short WhatsApp message (10-15 words, 1 question max)
Critic: Check hallucination risk, forbidden claims, tone, CTA spam
16.3 HTL Input (Context Compiler)
Always include:
System prompt (fixed)
BusinessConfig, SalesRules, ToneProfile, Guardrails
Last 8-12 messages
Rolling summary + slots + commitments
Timing variables: t (time since last user msg), f (response rate), service window status
Conditionally include:
Retrieved snippets (if triggered)
Knowledge chunks (FAQ/website) (if needed)
Enforce: MEMORY_BUDGET total_max = 2500 tokens
16.4 HTL Output Schema
{
  "should_send": true,
  "message_type": "TEXT",
  "reason_code": "CTA_PUSH",
  "cta_type": "APP_DOWNLOAD",
  "message_text": "App download kar lo, free demo milega: [LINK]",
  "confidence": 0.85,
  "retrieval_used": false,
  "input_tokens": 1200,
  "output_tokens": 50,
  "cost_usd": 0.008,
  "send_plan": "freeform",  # or "template"
  "state_patch": {
    "stage": "CTA_OFFERED",
    "status": "ENGAGED",
    "slots": {...},
    "commitments": {...},
    "cta_states": {"APP_DOWNLOAD": {"state": "OFFERED_ONCE"}},
    "followup_job": {"schedule_at": "2024-01-08T18:00Z"}
  },
  "handoff_required": false
}

16.5 Simple Mode Toggle
Setting: mode = HTL (default) or mode = SIMPLE_PROMPT
Simple mode: Single prompt for all messages (for testing/demos).

17) FOLLOW-UP LOGIC
17.1 Inside 24h Window
HTL decides:
Reply immediately
Stay silent
Schedule follow-up check job
Follow-up algorithm:
# Consider:
- t (time elapsed since last user msg)
- f (user response rate)
- stage urgency
- last message content

# Decide type:
- Soft ping
- Value add (testimonial, case study)
- Clarification
- Exit

17.2 Outside 24h Window
Templates only. Admin config defines:
Schedule steps: +2d, +5d, +7d
Template selection pool (utility templates)
If user replies, window reopens and scheduled templates canceled.

18) ESCALATION & HANDOFF
18.1 Triggers
Payment/booking failure
Angry sentiment
Complex question (3+ confused exchanges)
Explicit user request
Compliance risk
18.2 Handoff Context Package
{
  "escalation_reason": "payment_failure",
  "priority": "CRITICAL",
  "summary": "High intent. Payment failed. Offer UPI/alternate.",
  "key_slots": {"name": "Rajesh", "budget": 10000},
  "sentiment_trend": "frustrated_but_interested",
  "recommended_action": "Offer UPI or EMI",
  "conversation_value_score": 85
}

Stored in htl_decisions.handoff_context and shown in UI.
18.3 UI Display
Dashboard shows:
🔴 CRITICAL (2)
🟡 HIGH (5)
🟢 MEDIUM (12)
⚪ LOW (8)
18.4 Human Takeover Flow
Set status = NEEDS_HUMAN
Bot stops processing
Admin can type and send manual messages
Admin marks "resolved" to unlock

19) A/B TESTING FRAMEWORK
CREATE TABLE experiments (
  id UUID PRIMARY KEY,
  org_id UUID,
  name TEXT,
  variants JSONB,  -- {"control": {...}, "variant_a": {...}}
  active BOOLEAN,
  start_date TIMESTAMP,
  end_date TIMESTAMP
);

CREATE TABLE conversation_experiments (
  conversation_id UUID,
  experiment_id UUID,
  variant TEXT,
  PRIMARY KEY (conversation_id, experiment_id)
);

Test:
Message length (10 vs 20 words)
CTA timing (early vs late)
Tone (formal vs casual)
Follow-up intervals
Assignment: Deterministic hash on conversation_id for stable assignment.

20) CONFIG VERSIONING
business_profile = {
  "prompt_version": 3,
  "prompt_history": [
    {"version": 1, "updated_at": "2024-01-01", "updated_by": "user_id"},
    {"version": 2, "updated_at": "2024-01-05", "updated_by": "user_id"}
  ],
  "test_config_id": "uuid",  # Route 10% traffic to test config
  "test_traffic_percent": 10
}

1-click rollback if new config performs worse.

21) KNOWLEDGE STALENESS DETECTION
ALTER TABLE knowledge_docs ADD COLUMN last_verified TIMESTAMP;
ALTER TABLE knowledge_docs ADD COLUMN stale_alert BOOLEAN DEFAULT false;

Cron job: Monthly website check (pricing/terms/refund pages). If changed, set stale_alert = true.
HTL behavior: When stale_alert true, avoid stating hard numbers or escalate if user asks pricing/policy.

22) RELIABILITY
22.1 Webhook Send Retry
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type((ConnectionError, Timeout))
)
def send_whatsapp(phone, text):
    # Send logic

Record send_attempts and send_status in htl_decisions.
22.2 Failsafe (Dead Man's Switch)
try:
    decision = htl.think(context)
except Exception as e:
    log_critical_error(e)
    decision = simple_fallback_response(conversation)
    send_alert("HTL failure", conversation_id)

Fallback: Acknowledge, ask one simple question, stay safe.

23) COST TRACKING
ALTER TABLE htl_decisions ADD COLUMN input_tokens INT;
ALTER TABLE htl_decisions ADD COLUMN output_tokens INT;
ALTER TABLE htl_decisions ADD COLUMN cost_usd DECIMAL(10,4);

Dashboard shows:
Cost per conversation
Cost per won lead
ROI by lead_source

24) DATA DELETION
def delete_user_data(phone):
    # Anonymize phone, remove PII from slots
    conversation.contact_phone = hash(phone)
    conversation.slots = {"deleted": True}
    # Keep aggregated analytics
    audit_log.append({"action": "data_deletion", "phone": hash(phone)})


25) PERFORMANCE BUDGETS
slas:
  webhook_response: 100ms
  htl_decision: 3s
  message_send: 1s
  ui_load: 2s

monitoring:
  alert_if_p95_exceeds: true
  log_slow_queries: true


26) ADMIN UI
Page 1: Dashboard
KPIs: Active chats, Won, Lost, Dropped, Needs Human, Total chats, Total msgs
Charts: Chats per day, Conversion funnel, Cost metrics
Escalation queue panel (by priority)
Knowledge stale alerts
Page 2: Conversations (Inbox)
List: Filters (status/stage/lead_source/needs_human)
Click opens WhatsApp-style transcript
Shows: slots + confidence, CTA states, sentiment timeline, last HTL decision, handoff brief
Page 3: CRM
Columns: Name, Business, Email, Website, Phone, Status, Summary, Last Activity
Actions: Open conversation, Mark status, Takeover
Page 4: Sales Cycle (Kanban)
Columns = statuses
Drag cards to change status
Page 5: Calendar
List meetings booked by HTL
Sync status
Page 6: Settings
BusinessConfig editor (safe fields)
SalesRules, ToneProfile, Guardrails editors
Follow-up config (inside 24h: caps/gaps, outside 24h: template schedule)
Templates manager (sync from WhatsApp, category mapping)
MCP integrations (calendar, email)
Compliance (STOP detection, opt-out list, template enforcement)
Experiments management
Knowledge review alerts
Config versions + rollback

27) DATABASE SCHEMA (COMPLETE)
-- Auth
orgs (id, name, created_at)
users (id, org_id, email, password_hash, created_at)

-- Business Config
business_profiles (id, org_id, business_config_json, sales_rules_json, tone_profile_json, guardrails_json, mode, prompt_version, prompt_history, test_config_id, test_traffic_percent, updated_at)

-- Knowledge
knowledge_docs (id, org_id, source_type, title, content, metadata_json, embedding, last_verified, stale_alert, created_at)

-- Conversations
conversations (id, org_id, channel, contact_phone, lead_source, campaign_metadata, status, stage, owner_user_id, opted_out, last_user_message_at, last_bot_message_at, service_window_until, nudge_count_window, created_at, updated_at)

messages (id, org_id, conversation_id, role, msg_type, provider_message_id UNIQUE, text, media_url, created_at)

conversation_state (conversation_id PK, org_id, rolling_summary, slots_json, commitments_json, sentiment_history_json, cta_states_json, staleness_state, response_rate_json, risk_flags_json, last_intent, updated_at)

-- HTL
htl_decisions (id, org_id, conversation_id, trigger, should_send, message_type, reason_code, cta_type, message_text, pre_state_json, post_state_json, retrieval_used, confidence, input_tokens, output_tokens, cost_usd, send_attempts, send_status, error, handoff_required, handoff_priority, handoff_context_json, guardrail_result_json, created_at)

-- Templates & Followups
templates (id, org_id, name, provider_template_id, category, language, body_preview, variables_json, approval_status, quality_rating, created_at)

followup_configs (id, org_id, inside_window_json, outside_window_json, updated_at)

-- Scheduler
jobs (id, org_id, conversation_id, job_type, run_at, status, payload_json, created_at)

-- MCP
calendar_events (id, org_id, conversation_id, title, start_time, end_time, attendee_contact, provider_event_id, created_at)

-- A/B Testing
experiments (id, org_id, name, variants_json, active, start_date, end_date, created_at)
conversation_experiments (conversation_id, experiment_id, variant, assigned_at, PRIMARY KEY (conversation_id, experiment_id))

-- Analytics
conversation_patterns (id, org_id, pattern_type, description, frequency, example_conversation_ids, detected_at)

-- Audit
audit_logs (id, org_id, actor_type, actor_id, action, payload_json, created_at)


28) BACKEND FOLDER STRUCTURE
repo/
  apps/
    api/
      app/
        main.py
        config.py
        db.py
        deps.py
        
        routers/
          auth.py
          onboarding.py
          whatsapp_webhook.py
          conversations.py
          crm.py
          analytics.py
          settings.py
          templates.py
          calendar.py
        
        modules/
          channel/
            whatsapp_adapter.py
          
          policy/
            guardrails.py
            optout.py
            window.py
          
          state/
            store.py
            context_compiler.py
            memory_extractor.py
            retrieval.py
            staleness.py
            slot_extractor.py
            sentiment.py
            cta_machine.py
          
          htl/
            compiler.py
            planner.py
            writer.py
            critic.py
            schemas.py
            engine.py
          
          scheduler/
            enqueue.py
            jobs.py
          
          executor/
            sender.py
            actions.py
          
          crm/
            service.py
          
          analytics/
            cost.py
            service.py
          
          experiments/
            assign.py
          
          failsafe/
            fallback.py
          
          knowledge/
            freshness.py
          
          mcp/
            calendar.py
            email.py
            transcription.py
        
        models/
          enums.py
          tables.py
          schemas.py
        
        utils/
          logging.py
          time.py
          idempotency.py
      
      alembic/
        versions/
      
      tests/


29) FRONTEND FOLDER STRUCTURE
apps/web/
  app/
    login/
      page.tsx
    dashboard/
      page.tsx
    conversations/
      page.tsx
      [id]/page.tsx
    crm/
      page.tsx
    pipeline/
      page.tsx
    calendar/
      page.tsx
    settings/
      page.tsx
      business-config/page.tsx
      sales-rules/page.tsx
      tone/page.tsx
      guardrails/page.tsx
      followups/page.tsx
      templates/page.tsx
      experiments/page.tsx
      mcp/page.tsx
      compliance/page.tsx
  
  components/
    charts/
      ConversionFunnel.tsx
      ChatsPerDay.tsx
      CostMetrics.tsx
    tables/
      CRMTable.tsx
      ConversationsList.tsx
    chat/
      TranscriptView.tsx
      MessageBubble.tsx
    kanban/
      SalesPipeline.tsx
    ui/
      (shadcn components)
  
  lib/
    api.ts
    types.ts
    utils.ts


30) TECH STACK & DEPLOYMENT
Backend:
Python 3.11+
FastAPI
Uvicorn
PostgreSQL
SQLAlchemy 2.0 / SQLModel
Alembic
Redis
RQ (or Celery)
Frontend:
Next.js (App Router)
TypeScript
TailwindCSS
shadcn/ui
Recharts
Deployment:
API: Render / Fly.io
Web: Vercel
Postgres: Neon / Supabase / Render
Redis: Upstash / Render

31) MCP TOOLS (SCAFFOLDED)
# modules/mcp/calendar.py
async def create_calendar_event(title, start_time, attendee_email):
    # Google Calendar API integration
    pass

# modules/mcp/email.py
async def send_email(to, subject, body):
    # Gmail API / SendGrid integration
    pass

# modules/mcp/transcription.py
async def transcribe_voice_note(audio_url):
    # Whisper API / Deepgram integration
    pass

Note: Scaffolded for future use. MVP doesn't require full implementation.

32) MVP COMPLETION CRITERIA
✅ MVP is complete when:
WhatsApp inbound message triggers bot response inside 24h
Bot uses short messages (10-15 words), one question at a time
Conversations appear in UI with full transcript
CRM fields auto-populate from extracted slots (with confidence indicators)
Kanban updates status via drag-drop
Outside 24h template follow-up works (scheduled, sent, canceled on reply)
STOP opt-out stops all messaging immediately
Needs-human takeover works (bot stops, human can send, unlock after resolution)
Dashboard shows basic analytics (active chats, won, lost, dropped, cost)
HTL decisions logged with reasoning codes, cost tracking
Post-MVP (P1):
A/B testing enabled
Sentiment trend escalation
Slot confidence re-confirmation
Dynamic message budgets
Post-MVP (P2):
Knowledge staleness alerts
Config versioning with rollback
Conversation pattern clustering
Multi-language expansion

CRITICAL REMINDERS
Webhook must return 200 OK in <100ms (enqueue job, process async)
Idempotency is mandatory (unique constraint on provider_message_id)
Policy enforced in code, not LLM (24h window, opt-out, rate limits)
Memory budget strictly enforced (total_max = 2500 tokens)
Never truncate summary or slots (always keep critical state)
Staleness prevents spam (ARCHIVED = no outreach)
CTA state machine prevents CTA spam (OFFERED_TWICE = stop)
Slot confidence < 0.7 → re-confirm before major CTA
Cost tracking on every decision (input/output tokens, cost_usd)
Failsafe fallback (if HTL fails, use simple response, alert admin)
WhatsApp service conversations are FREE (inside 24h window)
Templates require pre-approval (12-48h wait)
Per-conversation locking (prevent race conditions)
Sentiment trend → escalation (declining = apologize, angry = escalate)
Dynamic message budget (hot leads get more budget)

APPENDIX: PRIORITY IMPLEMENTATION ORDER
P0 (Before Launch):
Onboarding flow + pre-run config generation
Webhook handling (fast response, idempotency)
Conversation creation + attribution
HTL pipeline (planner, writer, critic)
Memory system (summary, slots, commitments)
Staleness detection
CTA state machine
Policy guardrails module
Webhook send retry
Failsafe fallback
Basic Admin UI (Dashboard, Conversations, CRM)
P1 (Week 1 Post-Launch): 12. Slot confidence tracking + re-confirmation 13. Sentiment timeline + trend analysis 14. Handoff context package 15. Retrieval quality scoring 16. Cost tracking display
P2 (Month 1): 17. A/B testing framework 18. Dynamic message budget 19. Escalation priority queue 20. Multi-language expansion
P3 (Later): 21. Knowledge staleness detection 22. Config versioning + rollback 23. Conversation pattern clustering 24. Data deletion API 25. Performance monitoring

END OF SPEC v2.1
Status: Production-ready, complete, Antigravity IDE compatible.
Next Steps:
Generate SQLAlchemy models
Generate FastAPI routers
Generate HTL prompt templates
Generate Next.js UI components
Say "generate backend skeleton" or "generate frontend skeleton" to proceed.


SPEC v2.1 ERRORS & MISSTEPS (CRITICAL AUDIT)
🔴 CRITICAL ERRORS
1. WhatsApp Service Window Misconception
Error: Spec says service conversations are "FREE inside 24h window"
Reality Check:
Service conversations are ALWAYS free (user-initiated)
The 24h window determines IF you can send free-form messages
OUTSIDE 24h, you can ONLY send templates (which ARE charged)
Impact: HIGH - Cost model is correct, but explanation confusing
Fix: Clarify: "Inside 24h = freeform allowed (free), Outside 24h = templates only (charged)"

2. Staleness vs Window Confusion
Error: Staleness states (ACTIVE <6h, COOLING 6-24h) overlap with WhatsApp's 24h window
Problem:
WhatsApp window = 24h from user's LAST message (resets on every reply)
Staleness = time since last user message (doesn't reset)
These are measuring DIFFERENT things
Scenario: User replies at hour 5, hour 10, hour 15...
WhatsApp window: Always open (keeps resetting)
Staleness: Stays ACTIVE (multiple replies)
Fix: Rename staleness or clarify they measure different dimensions:
Staleness = "engagement freshness" (how recently active)
Window = "messaging permission" (can we send freeform?)

3. CTA State Machine Missing "RESET" Logic
Error: If CTA state = OFFERED_TWICE, bot stops offering that CTA forever
Problem: What if user comes back 2 months later and is ready?
Missing:
Time-based reset (after 30 days, reset to NOT_OFFERED)
Explicit user interest signal reset ("Actually, I'm interested now")
Fix: Add CTA state expiration or explicit reset triggers

4. Slot Confidence Overwrite Logic is Too Strict
Error: "Never overwrite high-confidence (0.8+) with low-confidence (<0.7)"
Problem: User: "My budget was 5000, but now I can do 10000"
Existing slot: {budget: 5000, confidence: 0.95}
New slot: {budget: 10000, confidence: 0.70}
System IGNORES new slot!
Fix: Add exception for explicit corrections or value changes

5. Memory Budget Too Small for Real Conversations
Error: Total budget = 2500 tokens
Problem:
Recent messages (8-12 turns @ 50 tokens each) = 600 tokens
Stable context = 500 tokens
Summary = 250 tokens
Slots = 200 tokens
Total = 1550 tokens (before retrieval/knowledge)
But if conversation has 50+ messages and HTL needs retrieval:
Can't fit enough context for good decisions
Will forget important details
Fix: Increase to 3500-4000 tokens OR implement more aggressive summarization

🟡 MEDIUM ISSUES
6. No Handling for Button/List Replies
Spec mentions: MessageType includes BUTTON_REPLY, LIST_REPLY
Missing: How to generate/send interactive messages (buttons, lists)
Fix: Add section on interactive message generation (WhatsApp supports this)

7. No Rate Limit Handling for LLM API
HTL calls LLM for: planning, writing, critic, extraction, summarization
Problem: If OpenAI/Anthropic rate limits hit, entire system blocks
Missing:
Exponential backoff for LLM calls
Fallback to simpler prompts if rate limited
Queue system for LLM calls
Fix: Add LLM rate limit handling strategy

8. Semantic Search Requires Embeddings
Spec says: "semantic_search(query, conversation_id, top_k=10)"
Missing:
Embedding generation for messages
Vector database (pgvector / Pinecone)
Embedding model choice (OpenAI / sentence-transformers)
Fix: Add embedding generation pipeline to message storage

9. No Webhook Signature Verification Details
Code shows: if not verify_signature(payload): return 401
Missing: HOW to verify (WhatsApp uses HMAC-SHA256 with secret)
Fix: Add webhook signature verification implementation

10. Follow-Up Job Scheduling Logic Incomplete
Spec says: "Schedule follow-up check job"
Missing:
When exactly? (After 2h? 6h? 12h?)
Algorithm to determine optimal follow-up time
Cancel logic if user replies before scheduled time
Fix: Add explicit follow-up timing algorithm

11. No Handling for User Editing/Deleting Messages
WhatsApp allows: Users to edit or delete sent messages
Problem: Bot might have already processed and responded
Missing:
Webhook events for message edits/deletes
Handling strategy (ignore? reprocess? flag inconsistency?)
Fix: Add message edit/delete event handling

12. Template Variables Not Mapped
Templates table has: variables_json
Missing: How HTL populates template variables from slots
Example: Template "Hi {name}, reminder about {product}"
HTL needs to map slots["name"] → template variable
Fix: Add template variable population logic

13. No Multi-Turn CTA Flows
Current CTA: Single-step (send link, user clicks/doesn't click)
Real World: Multi-step flows
"Book a call" → User clicks → Calendar picker → Confirmation
"Make payment" → User clicks → Payment page → Success/Failure webhook
Missing: How to track multi-step CTA completion
Fix: Add CTA completion webhooks and multi-step tracking

🟢 MINOR ISSUES
14. No Timezone Handling for Follow-Ups
User in Mumbai (IST), bot schedules follow-up at 2 AM local time
Missing: Respect user timezone for scheduled messages
Fix: Add timezone awareness to job scheduler

15. No Image/Document Handling in HTL
User sends: Product image asking "Price for this?"
HTL receives: Only text context, no image analysis
Missing: Vision model integration for image understanding
Fix: Add optional vision model for image analysis (later enhancement)

16. No Duplicate Lead Detection
Scenario: User messages from 2 different numbers (work phone, personal phone)
Problem: Creates 2 separate conversations, duplicate CRM entries
Missing: Lead deduplication by email/name
Fix: Add deduplication logic in CRM (later enhancement)

17. No Conversation Merging
Scenario: User starts new conversation about same topic
Problem: Bot doesn't remember previous conversation
Missing: Option to merge/link related conversations
Fix: Add conversation linking in CRM UI (later enhancement)

18. No Bulk Operations
Admin wants: "Mark all DROPPED leads as LOST"
Missing: Bulk status updates, bulk message sending
Fix: Add bulk operations to CRM UI (later enhancement)

19. No Export Functionality
Admin wants: Export conversations to CSV, export analytics
Missing: Data export endpoints
Fix: Add export APIs for conversations, CRM, analytics (later enhancement)

20. No Notification System for Admins
Critical escalation happens, admin doesn't know
Missing:
Push notifications
Email alerts
Slack/Discord webhooks
Fix: Add notification system for critical events (later enhancement)

❌ LOGICAL INCONSISTENCIES
21. Staleness "ARCHIVED" Conflicts with "Never Forget"
Spec says:
"Store full transcript forever"
"ARCHIVED state: no proactive outreach"
Inconsistency: Is ARCHIVED conversation still accessible? Can user reactivate it?
Fix: Clarify ARCHIVED means "bot won't initiate" but conversation still exists and responds if user returns

22. "Simple Mode" Underspecified
Spec says: mode = SIMPLE_PROMPT (single prompt for all messages)
Missing: What does this prompt look like? What context does it get?
Fix: Add example simple prompt template

23. Handoff Context Stored But Not Used
Spec stores: handoff_context in htl_decisions table
Missing: How does human agent UI display this prominently?
Fix: Ensure UI shows handoff brief as first thing human sees