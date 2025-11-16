# BLV Dashboard

Dashboard interactif pour analyse Business Logic Vulnerabilities avec chat IA Claude Sonnet 4.5, gestion mindset, et parser Burp Suite.

## Features

- **Chat IA Streaming** - Chat temps réel avec Claude Sonnet 4.5 (streaming SSE)
- **Mémoire Persistante** - Historique conversations stocké en PostgreSQL
- **Mindset Configuration** - Édition prompt système avec templates prédéfinis
- **Burp Suite Parser** - Parse requêtes HTTP brutes, détection GraphQL automatique
- **Design Clean** - Interface DaisyUI (palette zinc), responsive, sidebar navigation

## Stack Technique

**Backend:**
- Flask 3.0.0
- PostgreSQL (local)
- Anthropic Claude API (Sonnet 4.5)

**Frontend:**
- Alpine.js 3.13.3
- DaisyUI 4.4.19
- TailwindCSS
- AutoAnimate

## Installation

### 1. Prérequis

- Python 3.13+
- PostgreSQL 14+ (local)
- Claude API Key (Anthropic)

### 2. Installer dépendances

```bash
pip install -r requirements.txt
```

### 3. Configuration

Éditer `.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=gestion
DB_USER=postgres
DB_PASSWORD=Voiture789
DB_SCHEMA=api
```

### 4. Initialiser database

```bash
python init_db.py
```

Résultat attendu:
```
Connected to PostgreSQL database 'gestion'
[OK] Schema 'api' created successfully
[OK] Tables created: conversations, http_requests, messages, settings
[SUCCESS] Database initialization completed successfully!
```

### 5. Lancer application

```bash
python app.py
```

Ouvrir: http://localhost:5000

## Configuration API Key

1. Cliquer sur "API Key" dans la sidebar
2. Entrer votre Anthropic API key (`sk-ant-...`)
3. Sauvegarder

## Utilisation

### Chat IA

1. Page principale (`/`)
2. Envoyer message
3. Claude répond en streaming (fluide, temps réel)
4. Historique sauvegardé automatiquement
5. Créer nouvelles conversations avec "New Chat"

### Mindset

1. Aller `/mindset`
2. Éditer prompt système (définit comportement Claude)
3. Utiliser templates rapides (BLV Expert, Pentester, etc.)
4. Sauvegarder
5. Prompt appliqué à toutes futures conversations

### Burp Parser

1. Aller `/burp-parser`
2. Copier requête HTTP brute depuis Burp Suite
3. Coller dans textarea
4. Cliquer "Parse & Save"
5. Preview affiche données structurées (method, url, headers, GraphQL operation)
6. Historique visible en bas (50 dernières requêtes)

**Exemple requête PayPal:**
```http
POST /graphql/ HTTP/2
Host: www.paypal.com
Content-Type: application/json

{"operationName":"approveMemberPayment",...}
```

Détecte automatiquement:
- GraphQL operation: `approveMemberPayment`
- Method: `POST`
- Host: `www.paypal.com`
- Headers: 67 parsés
- Body JSON

## Structure Database

**Schema:** `api`

**Tables:**
- `settings` - API key, system prompt
- `conversations` - Conversations chat
- `messages` - Messages (user/assistant)
- `http_requests` - Requêtes Burp parsées

## API Routes

### Settings
- `GET /api/settings/system-prompt`
- `POST /api/settings/system-prompt`
- `GET /api/settings/api-key`
- `POST /api/settings/api-key`

### Conversations
- `GET /api/conversations`
- `POST /api/conversations`
- `GET /api/conversations/<id>/messages`

### Chat
- `POST /api/chat` (SSE streaming)

### Burp
- `POST /api/burp/parse`
- `GET /api/burp/requests`

## Architecture

Voir `ARCHITECTURE.md` pour détails complets:
- Structure fichiers
- Schema database
- Services layer
- Conventions code
- Workflow développement

## Développement

### Ajouter nouvelle feature

1. Backend: route API dans `app.py`
2. Service: logique métier dans `services.py`
3. Model (si besoin): `models.py`
4. Frontend: page template `templates/pages/`
5. Update `ARCHITECTURE.md`

### Tester

```bash
# API
curl http://localhost:5000/api/conversations

# Parser
curl -X POST http://localhost:5000/api/burp/parse \
  -H "Content-Type: application/json" \
  -d '{"raw_request":"POST /test HTTP/1.1\nHost: example.com\n\n"}'
```

## Sécurité

- API key jamais exposée (masquée dans GET)
- PostgreSQL local (pas internet)
- `.gitignore` protège `.env`
- Pas de secrets hardcodés

## Troubleshooting

**Database connection error:**
```bash
# Vérifier PostgreSQL actif
pg_ctl status

# Tester connexion
python -c "import psycopg2; psycopg2.connect('postgresql://postgres:Voiture789@localhost:5432/gestion')"
```

**Flask port occupé:**
```bash
# Changer port dans app.py
app.run(debug=True, port=5001)
```

**API key non configurée:**
- Aller sidebar → API Key
- Entrer clé Anthropic valide

## Conventions

- **Python**: snake_case, PascalCase classes
- **Frontend**: Alpine.js, optimistic UI, palette zinc
- **Database**: schema `api`, indexes sur FK/dates

## Licence

Projet interne BLV. Non distribué.

---

**Version:** 1.0
**Date:** 2025-11-16
**Stack:** Flask + Alpine.js + PostgreSQL + Claude Sonnet 4.5
