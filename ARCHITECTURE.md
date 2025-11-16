# ARCHITECTURE - BLV Dashboard

> **Stack:** Flask + Alpine.js + DaisyUI + PostgreSQL
> **Database:** Local PostgreSQL (localhost:5432, db=gestion, schema=api)
> **AI:** Claude Sonnet 4.5 (Anthropic API)

---

## FEATURES EXISTANTES

### 1. Chat AI avec Streaming
- Interface chat temps réel avec Claude Sonnet 4.5
- Streaming SSE (Server-Sent Events) pour réponses fluides
- Historique conversations stocké en base
- Création conversations multiples
- Mémoire persistante (messages DB)

### 2. Mindset Configuration
- Édition prompt système (system prompt)
- Templates prédéfinis (BLV Expert, Pentester, Researcher, General)
- Sauvegarde en base PostgreSQL
- Preview temps réel
- Character counter

### 3. Burp Suite Parser
- Parse requêtes HTTP brutes (Burp Suite)
- Détection automatique GraphQL
- Extraction headers/body/method/url
- Historique requêtes parsées
- Preview structuré

---

## STRUCTURE FICHIERS

```
BLV-Dashboard/
├── app.py                      # Flask app principal (routes)
├── config.py                   # Configuration (DB, env)
├── models.py                   # Models PostgreSQL (ORM-like)
├── services.py                 # Logique métier
├── init_db.py                  # Script init schema PostgreSQL
├── init_db.sql                 # SQL schema (backup)
├── requirements.txt            # Dépendances Python
├── .env                        # Variables environnement
├── .gitignore
│
├── templates/
│   ├── base.html              # Template base (sidebar, navbar, modals)
│   └── pages/
│       ├── chat.html          # Page chat IA
│       ├── mindset.html       # Page mindset config
│       └── burp_parser.html   # Page parser Burp
│
└── static/
    ├── js/                    # (vide, Alpine.js inline)
    └── css/                   # (vide, DaisyUI CDN)
```

---

## DATABASE SCHEMA (PostgreSQL)

**Schema:** `api`

### Tables

#### `api.settings`
```sql
- key: VARCHAR(255) PRIMARY KEY
- value: TEXT
- updated_at: TIMESTAMP
```
**Usage:** Stocke API key Claude + system_prompt

#### `api.conversations`
```sql
- id: SERIAL PRIMARY KEY
- title: VARCHAR(500)
- created_at: TIMESTAMP
```
**Usage:** Conversations chat IA

#### `api.messages`
```sql
- id: SERIAL PRIMARY KEY
- conversation_id: INTEGER FK
- role: VARCHAR(50)  -- 'user' | 'assistant'
- content: TEXT
- created_at: TIMESTAMP
```
**Usage:** Messages chat (historique)

#### `api.http_requests`
```sql
- id: SERIAL PRIMARY KEY
- raw_request: TEXT
- method: VARCHAR(10)
- url: TEXT
- host: VARCHAR(500)
- path: TEXT
- headers_json: JSONB
- body: TEXT
- graphql_operation: VARCHAR(255)
- graphql_query: TEXT
- parsed_at: TIMESTAMP
```
**Usage:** Requêtes Burp parsées

---

## ROUTES API

### Settings
- `GET /api/settings/api-key` - Get API key (masked)
- `POST /api/settings/api-key` - Set API key
- `GET /api/settings/system-prompt` - Get system prompt
- `POST /api/settings/system-prompt` - Update system prompt

### Conversations
- `GET /api/conversations` - Liste conversations
- `POST /api/conversations` - Créer conversation
- `GET /api/conversations/<id>/messages` - Messages conversation

### Chat
- `POST /api/chat` - Envoyer message (streaming SSE)

### Burp Parser
- `POST /api/burp/parse` - Parser requête HTTP
- `GET /api/burp/requests` - Historique requêtes

---

## ROUTES PAGES

- `/` - Chat AI (page principale)
- `/mindset` - Configuration mindset
- `/burp-parser` - Parser Burp Suite

---

## SERVICES LAYER

### `ChatService`
- `get_system_prompt()` / `set_system_prompt()`
- `get_api_key()` / `set_api_key()`
- `create_conversation()` / `get_conversations()`
- `get_conversation_messages()` / `save_message()`

### `BurpParserService`
- `parse_http_request(raw)` - Parse HTTP request
- `save_request(raw)` - Parse + save DB
- `get_all_requests()` / `get_request(id)`

---

## COMPONENTS HTML (Réutilisables)

### `base.html`
- Sidebar navigation (DaisyUI drawer)
- Modal API key configuration
- Alpine.js store global `app`

**Alpine Store `app`:**
```js
{
  showApiKeyModal: false,
  apiKeyInput: '',
  saveApiKey()
}
```

---

## ALPINE.JS STORES

### Global Store (`base.html`)
- `app.showApiKeyModal` - Toggle modal API key
- `app.apiKeyInput` - Input API key
- `app.saveApiKey()` - Save API key

### Page-specific (inline x-data)
- `chatApp()` - Chat page (templates/pages/chat.html)
- `mindsetApp()` - Mindset page (templates/pages/mindset.html)
- `burpParserApp()` - Burp parser page (templates/pages/burp_parser.html)

---

## TECHNOLOGIES

**Backend:**
- Flask 3.0.0
- psycopg2-binary 2.9.9
- anthropic 0.39.0 (Claude API)
- python-dotenv 1.0.0

**Frontend:**
- Alpine.js 3.13.3 (CDN)
- DaisyUI 4.4.19 (CDN)
- TailwindCSS (CDN)
- AutoAnimate 1.0.0-beta.6 (CDN)

**Database:**
- PostgreSQL 14+ (local)

---

## CONVENTIONS

### Python
- Fichiers: snake_case.py
- Classes: PascalCase
- Fonctions: snake_case
- Routes: max 10-15 lignes (appels services)

### Frontend
- Alpine.js: @click/@submit (pas onclick)
- Optimistic UI (update local avant fetch)
- DaisyUI theme="light"
- Palette zinc (50/100/200/300/400/500/900)

### Database
- Schema `api` (isolé)
- Indexes sur FK et dates
- JSONB pour données structurées (headers)

---

## FEATURES GRAPHQL PARSER

**Détection automatique:**
- Si body contient `query` ou `mutation`
- Parse JSON → extrait `operationName` + `query`
- Stocke séparément dans `graphql_operation` + `graphql_query`

**Exemple requête PayPal:**
```
Operation: approveMemberPayment
Type: GraphQL Mutation
Variables: token, selectedFundingOptionId, etc.
```

---

## SÉCURITÉ

- API key masquée dans GET (affiche uniquement 10 premiers + 4 derniers chars)
- Pas de secrets hardcodés (`.env`)
- `.gitignore` protège `.env`
- PostgreSQL local (pas exposé internet)

---

## WORKFLOW DÉVELOPPEMENT

### Ajouter nouvelle feature:
1. Créer route API (`app.py`)
2. Ajouter logique service (`services.py`)
3. Si besoin model DB (`models.py`)
4. Créer page template (`templates/pages/`)
5. Update `ARCHITECTURE.md`

### Ajouter nouveau parser:
1. Ajouter méthode `BurpParserService`
2. Créer route `/api/burp/...`
3. Update frontend `burp_parser.html`

---

## DÉMARRAGE PROJET

```bash
# 1. Installer dépendances
pip install -r requirements.txt

# 2. Configurer .env
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=gestion
# DB_USER=postgres
# DB_PASSWORD=Voiture789

# 3. Initialiser database
python init_db.py

# 4. Lancer app
python app.py

# 5. Ouvrir http://localhost:5000
```

---

## TESTS

### Test Chat Streaming:
1. Configurer API key (sidebar → API Key)
2. Aller page Chat
3. Envoyer message
4. Vérifier streaming fluide

### Test Burp Parser:
1. Copier requête Burp
2. Aller page Burp Parser
3. Coller → Parse & Save
4. Vérifier preview + history

### Test Mindset:
1. Aller page Mindset
2. Modifier prompt
3. Save
4. Vérifier dans chat (nouveau message utilise prompt)

---

**Version:** 1.0
**Date:** 2025-11-16
**Statut:** Production-Ready
