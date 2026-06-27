<div align="center">

# QuickBite Nepal

**Restaurant delivery platform built with Django**

Browse restaurants, place orders, pay with local wallets, and track deliveries — with dedicated experiences for customers, restaurant partners, delivery riders, and administrators.

<br>

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.x-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14+-red)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-Educational-lightgrey)](#license)

**[Overview](#project-overview)** ·
**[Features](#features)** ·
**[Architecture](#architecture)** ·
**[Installation](#installation)** ·
**[API](#rest-api)** ·
**[Contributing](#contributing)** ·
**[Ownership](#repository-ownership)**

<br>

<img src="Photos%20for%20Readme/Screenshot%202026-06-27%20092442.png" alt="QuickBite homepage" width="900">

*Homepage — customer-facing landing experience*

</div>

---

## Table of contents

- [Short description](#short-description)
- [Project overview](#project-overview)
- [Features](#features)
- [Architecture](#architecture)
- [Folder structure](#folder-structure)
- [Technology stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the project](#running-the-project)
- [User roles](#user-roles)
- [Application modules](#application-modules)
- [Database overview](#database-overview)
- [REST API](#rest-api)
- [Project workflow](#project-workflow)
- [Screenshots](#screenshots)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Repository ownership](#repository-ownership)
- [Git workflow](#git-workflow)
- [Commit convention](#commit-convention)
- [Development guidelines](#development-guidelines)
- [License](#license)
- [Authors](#authors)
- [Acknowledgements](#acknowledgements)
- [Project status](#project-status)

---

## Short description

**QuickBite** is a full-stack food delivery web application developed as an academic group project under **Bachelor of Computer Application**, targeting the Nepal market. It connects **customers**, **restaurant partners**, and **delivery riders** through a Django monolith with a REST API, role-based authentication, local payment methods (eSewa, Khalti, cash on delivery), email notifications, operational analytics, and a custom admin operations console.

The platform is built for Pokhara and broader Nepal use cases: NPR pricing, `Asia/Kathmandu` timezone, Nepali payment gateways, and multi-role login flows (customer, restaurant, rider).

---

## Project overview

| Actor | Experience |
|-------|------------|
| **Customer** | Browse restaurants, build a cart, checkout, pay, track delivery on a live map, manage profile and order history |
| **Restaurant partner** | Register, subscribe to a plan, manage menu items, accept/reject orders, view earnings |
| **Delivery rider** | Register, receive delivery assignments, update status, view earnings |
| **Administrator** | Custom Django admin with analytics dashboard, data management hubs, email health monitoring |
| **API consumer** | Versioned REST API (`/api/v1/`) with JWT authentication for mobile or third-party clients |

**Core domains:** authentication & roles, restaurant & menu catalog, ordering & tracking, payments & invoices, partner & rider operations, analytics (PostHog), transactional email.

---

## Features

| Area | Capabilities |
|------|----------------|
| **Authentication** | Email-based signup/login, password reset, OTP verification, role-based users (`CUSTOMER`, `RESTAURANT`, `RIDER`, `ADMIN`) |
| **Restaurant management** | Restaurants, cuisines, food items, availability, ratings metadata |
| **Menu management** | Partner menu CRUD, seed commands, category & food-type fields |
| **Search & discovery** | Restaurant listing, detail pages, category filters |
| **Reviews & favorites** | Customer reviews and favorite restaurants/food items |
| **Cart & checkout** | Session-based cart, delivery details, coupon support, multi-step checkout |
| **Orders** | Full lifecycle statuses, order items, tracking timeline, support tickets |
| **Coupons** | Percentage/fixed discounts with validity and usage limits |
| **Payments** | eSewa, Khalti, cash on delivery; invoices and payment status tracking |
| **Partner dashboard** | Registration, subscription plans, order management, analytics views |
| **Rider dashboard** | Registration, delivery assignments, GPS fields, earnings |
| **Admin dashboard** | Custom `QuickBiteAdminSite`, KPI analytics, model management hubs |
| **Analytics** | PostHog integration, page-view middleware, export utilities |
| **Email notifications** | Welcome, order, payment, partner/rider approval templates |
| **REST API** | DRF viewsets for all major resources, JWT auth, throttling, filtering |
| **Role-based access** | Permissions enforced in API and web views per user role |
| **Responsive UI** | Bootstrap 5, custom CSS/JS, mobile-oriented layout |
| **Error handling** | Custom 404/500 templates |
| **Legal & support pages** | FAQ, privacy, terms, refund policy, contact form |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Client (Browser / API)                       │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Django views │     │  DRF API /v1/   │     │ Custom Admin UI │
│  + Templates  │     │  JWT + ViewSets │     │ + Analytics     │
└───────┬───────┘     └────────┬────────┘     └────────┬────────┘
        │                      │                       │
        └──────────────────────┼───────────────────────┘
                               ▼
                 ┌─────────────────────────┐
                 │   Business logic layer   │
                 │  services · selectors    │
                 │  signals · middleware    │
                 └─────────────┬───────────┘
                               ▼
                 ┌─────────────────────────┐
                 │   Django ORM / Models    │
                 └─────────────┬───────────┘
                               ▼
                 ┌─────────────────────────┐
                 │      PostgreSQL          │
                 └─────────────────────────┘
```

| Layer | Implementation |
|-------|----------------|
| **Backend** | Django 5.x apps (`users`, `core`, `restaurant`, `orders`, `payments`, `partners`, `riders`, `analytics`, `api`, `accounts`) |
| **Frontend** | Server-rendered Django templates, Bootstrap 5, vanilla JavaScript (`cart.js`, `checkout.js`, `payment.js`, Leaflet for maps) |
| **API** | Django REST Framework + SimpleJWT |
| **Authentication** | Custom `users.User` model, email login, JWT for API, session auth for web |
| **Database** | PostgreSQL (configured via environment variables) |
| **Static / media** | WhiteNoise (production), `core/static/`, uploaded `media/` |
| **Email** | SMTP (configurable) with HTML templates in `templates/emails/` |
| **Analytics** | PostHog SDK + middleware (optional, env-driven) |
| **Admin** | Custom admin site (`core/admin_site.py`) replacing default Django admin branding |

---

## Folder structure

```text
QuickBite/
├── README.md
├── Documentation/              # Proposal & defense documents
├── Photos for Readme/            # Screenshots for documentation
└── quickbite/                    # Django project root
    ├── manage.py
    ├── requirements.txt
    ├── .env                      # Local secrets (not committed)
    ├── quickbite/                # Project configuration package
    │   ├── settings/             # base · development · staging · production
    │   ├── urls.py               # Root URL routing
    │   ├── wsgi.py
    │   └── asgi.py
    ├── accounts/                 # Auth-related views & URL bridges
    ├── users/                    # Custom user model, OTP, email services
    ├── core/                     # Marketing pages, admin platform, shared UI
    │   ├── templates/            # base, auth, orders, restaurants, admin, components
    │   ├── static/               # CSS, JS, images
    │   └── management/commands/  # superuser, roles, DB verification
    ├── restaurant/               # Restaurant & menu domain
    │   ├── services/
    │   ├── selectors/
    │   └── migrations/
    ├── orders/                   # Cart, checkout, tracking, order services
    │   ├── services/
    │   └── migrations/
    ├── payments/                 # eSewa/Khalti/COD, invoices, coupons
    │   ├── templates/payments/
    │   └── migrations/
    ├── partners/                 # Restaurant partner onboarding & dashboard
    │   └── templates/partners/
    ├── riders/                   # Rider registration & delivery
    │   ├── services/
    │   └── templates/riders/
    ├── analytics/                # PostHog, events, middleware, export
    ├── api/                      # REST API serializers, viewsets, permissions
    ├── templates/                # Global email & admin template overrides
    │   └── emails/
    ├── media/                    # Uploaded images (gitignored)
    ├── staticfiles/              # collectstatic output (gitignored)
    ├── logs/                     # Application logs
    └── docs/                     # Internal analytics & QA documentation
```

---

## Technology stack

| Category | Technologies |
|----------|--------------|
| **Language** | Python 3.11+ |
| **Backend framework** | Django 5.x |
| **API** | Django REST Framework, SimpleJWT, django-filter, django-cors-headers |
| **Database** | PostgreSQL (`psycopg2-binary`, `dj-database-url`) |
| **Frontend** | HTML5, CSS3, JavaScript, Bootstrap 5, Leaflet + OpenStreetMap |
| **Images** | Pillow |
| **Configuration** | python-decouple, `.env` |
| **Email** | Django SMTP backend |
| **Payments** | eSewa, Khalti (Nepal), cash on delivery |
| **Analytics** | PostHog (optional) |
| **Production server** | Gunicorn, WhiteNoise |
| **Caching (production)** | django-redis (configured in production settings) |
| **Export** | openpyxl (analytics export) |
| **Version control** | Git, GitHub |

---

## Installation

### Prerequisites

- Python 3.11 or newer
- PostgreSQL 14+
- Git

### Step-by-step

```bash
# 1. Clone the repository
git clone https://github.com/Bachelor-Of-Computer-Application/Alpha_Devs.git
cd Alpha_Devs/quickbite

# 2. Create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment (see Configuration section)
# Create quickbite/.env with database and secret settings

# 5. Apply database migrations
python manage.py migrate

# 6. (Optional) Seed payment methods and demo menu
python manage.py seed_payment_methods
python manage.py seed_quickbite_menu

# 7. Create an admin user
python manage.py createsuperuser
# Or use the management command:
python manage.py ensure_superuser

# 8. Run the development server
python manage.py runserver
```

Open **http://127.0.0.1:8000** in your browser.

---

## Configuration

Settings are loaded from `quickbite/quickbite/settings/` based on `DJANGO_ENV` (`development` · `staging` · `production`). Create `quickbite/.env` in the project root.

### Essential variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key — **required in production** |
| `DEBUG` | `True` for local development only |
| `DJANGO_ENV` | `development` (default), `staging`, or `production` |
| `DB_ENGINE` | `django.db.backends.postgresql` |
| `DB_NAME` | Database name |
| `DB_USER` | Database user |
| `DB_PASSWORD` | Database password |
| `DB_HOST` | Database host (default `localhost`) |
| `DB_PORT` | Database port (default `5432`) |

### Email

| Variable | Description |
|----------|-------------|
| `EMAIL_BACKEND` | e.g. `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | SMTP host |
| `EMAIL_PORT` | SMTP port |
| `EMAIL_HOST_USER` | SMTP username |
| `EMAIL_HOST_PASSWORD` | SMTP password |
| `DEFAULT_FROM_EMAIL` | Sender address |

### Payments

| Variable | Description |
|----------|-------------|
| `KHALTI_PUBLIC_KEY` | Khalti public key |
| `KHALTI_SECRET_KEY` | Khalti secret key |
| `ESEWA_MERCHANT_CODE` | eSewa merchant code |
| `ESEWA_SECRET_KEY` | eSewa secret key |

### Analytics (optional)

| Variable | Description |
|----------|-------------|
| `POSTHOG_API_KEY` | PostHog project API key |
| `POSTHOG_HOST` | PostHog host URL |
| `POSTHOG_PROJECT_ID` | PostHog project ID |

### Static & media

| Setting | Value |
|---------|-------|
| `STATIC_URL` | `/static/` |
| `STATIC_ROOT` | `quickbite/staticfiles/` |
| `MEDIA_URL` | `/media/` |
| `MEDIA_ROOT` | `quickbite/media/` |

---

## Running the project

All commands run from the `quickbite/` directory with the virtual environment activated.

```bash
# Development server
python manage.py runserver

# Database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files (production)
python manage.py collectstatic --noinput

# Run tests
python manage.py test

# Verify database connectivity
python manage.py verify_database

# Check SMTP configuration
python manage.py check_smtp
```

| URL | Purpose |
|-----|---------|
| `/` | Homepage |
| `/admin/` | Operations admin |
| `/accounts/` | Authentication |
| `/orders/` | Cart, checkout, tracking |
| `/partners/` | Partner portal |
| `/riders/` | Rider portal |
| `/api/v1/` | REST API root |

---

## User roles

| Role | Responsibilities | Access |
|------|------------------|--------|
| **Customer** | Browse, order, pay, track, review | Web UI, customer API profile |
| **Restaurant owner** | Manage menu, accept orders, view earnings | Partner dashboard, restaurant login |
| **Delivery rider** | Accept deliveries, update GPS/status | Rider dashboard, rider login |
| **Administrator** | Platform oversight, analytics, data management | Custom admin, superuser privileges |

Permissions are enforced through the custom `User.role` field, DRF permission classes, and view-level decorators.

---

## Application modules

### `accounts`
Authentication views and URL wiring that complement the `users` app (login flows, email verification pages).

### `users`
Custom `User` model (`AUTH_USER_MODEL`), email-based authentication, OTP services, email dispatcher, SMTP health checks, and profile templates.

### `core`
Marketing pages (home, about, services, contact, legal), shared templates (`base.html`, components), static assets, custom admin site, analytics dashboard, error handlers, and management commands.

### `restaurant`
Restaurant, `FoodItem`, `Cuisine`, `Review`, and `Favorite` models; menu services; seed commands; URL redirects to core restaurant templates.

### `orders`
`Order`, `OrderItem`, `OrderTracking`, `SupportTicket` models; cart, checkout, payment step, order confirmation, live tracking (Leaflet map API), coupon and order services.

### `payments`
`Payment`, `PaymentMethod`, `Invoice`, `Coupon` models; eSewa integration; payment result templates; seed commands for payment methods.

### `partners`
`RestaurantPartner`, `PartnerSubscription`, earnings models; partner registration, dashboard, menu management, and order action views.

### `riders`
`Rider`, `Delivery`, `RiderEarnings` models; rider registration and dashboard; delivery service layer.

### `analytics`
PostHog middleware, event services, signals, queries, export utilities, and admin-facing analytics context.

### `api`
REST API with JWT authentication — viewsets for users, restaurants, orders, payments, riders, deliveries, coupons, reviews, and favorites.

---

## Database overview

| Model | App | Purpose |
|-------|-----|---------|
| `User` | users | Email-based user with role |
| `CustomerProfile` / `RestaurantProfile` / `RiderProfile` | users | Role-specific profile data |
| `Restaurant`, `FoodItem`, `Cuisine` | restaurant | Catalog |
| `Review`, `Favorite` | restaurant | Social features |
| `Order`, `OrderItem` | orders | Purchase records |
| `OrderTracking` | orders | Delivery timeline |
| `SupportTicket` | orders | Customer support |
| `Payment`, `PaymentMethod`, `Invoice` | payments | Transactions |
| `Coupon` | payments | Discounts |
| `RestaurantPartner`, `PartnerSubscription` | partners | Partner accounts |
| `RestaurantEarnings` | partners | Partner revenue |
| `Rider`, `Delivery`, `RiderEarnings` | riders | Fleet operations |

Cart state is handled in the **orders** flow (session-based cart view and `cart.js`), not a separate database cart app.

---

## REST API

**Base URL:** `/api/v1/`

### Authentication

- **JWT** via `djangorestframework-simplejwt`
- Obtain token: `POST /api/v1/auth/token/`
- Refresh token: `POST /api/v1/auth/token/refresh/`
- Registration: `/api/v1/auth/register/`
- Default permission: `IsAuthenticated`
- Throttling: 100/hour (anonymous), 1000/hour (authenticated)

### Resource endpoints (router)

| Resource | Endpoint prefix |
|----------|-----------------|
| Users & profiles | `/users/`, `/customer-profiles/`, `/restaurant-profiles/`, `/rider-profiles/` |
| Restaurants | `/restaurants/`, `/food-items/`, `/cuisines/` |
| Social | `/reviews/`, `/favorites/` |
| Orders | `/orders/`, `/support-tickets/` |
| Payments | `/payments/`, `/payment-methods/`, `/invoices/`, `/coupons/` |
| Riders | `/riders/`, `/deliveries/`, `/rider-earnings/` |

Supports pagination (20 per page), filtering, search, and ordering via `django-filter`.

---

## Project workflow

### Customer journey

```
Home → Restaurants → Menu → Cart → Checkout (delivery) → Payment → Confirmation → Live tracking
```

### Partner journey

```
Partner registration → Admin approval → Dashboard → Menu management → Accept/prepare orders
```

### Rider journey

```
Rider registration → Admin approval → Dashboard → Accept delivery → Update status → Earnings
```

### Order lifecycle

`pending` → `confirmed` → `preparing` → `ready` → `picked_up` → `in_transit` → `delivered`

(Also: `cancelled`, `failed`)

### Payment flow

Select method (eSewa / Khalti / COD) → Process via gateway or mark pending → Invoice generated → Status updated on order

### Admin flow

Login → Platform overview KPIs → Analytics dashboard → Data management hubs → Model CRUD

---

## Screenshots

### Marketing & authentication

<table>
<tr>
<td width="50%"><img src="Photos%20for%20Readme/Screenshot%202026-06-27%20092442.png" alt="Homepage"><br><sub><b>Homepage</b> — hero and primary CTAs</sub></td>
<td width="50%"><img src="Photos%20for%20Readme/Screenshot%202026-06-27%20092511.png" alt="Footer and CTA"><br><sub><b>Footer</b> — newsletter, links, payment badges</sub></td>
</tr>
<tr>
<td><img src="Photos%20for%20Readme/Screenshot%202026-06-27%20092604.png" alt="About page"><br><sub><b>About</b> — mission, vision, stats</sub></td>
<td><img src="Photos%20for%20Readme/Screenshot%202026-06-27%20092640.png" alt="Services page"><br><sub><b>Services</b> — customer, partner, rider offerings</sub></td>
</tr>
<tr>
<td><img src="Photos%20for%20Readme/Screenshot%202026-06-27%20092709.png" alt="Contact page"><br><sub><b>Contact</b> — form and Pokhara office details</sub></td>
<td><img src="Photos%20for%20Readme/Screenshot%202026-06-27%20092734.png" alt="Sign up"><br><sub><b>Sign up</b> — customer registration</sub></td>
</tr>
<tr>
<td colspan="2" align="center"><img src="Photos%20for%20Readme/Screenshot%202026-06-27%20092749.png" alt="Login" width="80%"><br><sub><b>Login</b> — customer, restaurant, and rider entry points</sub></td>
</tr>
</table>

### Ordering, payments & tracking

<table>
<tr>
<td width="50%"><img src="Photos%20for%20Readme/Screenshot%202026-06-27%20092948.png" alt="Payment selection"><br><sub><b>Payment</b> — eSewa, Khalti, COD</sub></td>
<td width="50%"><img src="Photos%20for%20Readme/Screenshot%202026-06-27%20093012.png" alt="Order confirmed"><br><sub><b>Order confirmed</b> — summary and track CTA</sub></td>
</tr>
<tr>
<td><img src="Photos%20for%20Readme/Screenshot%202026-06-27%20093053.png" alt="Order tracking timeline"><br><sub><b>Live tracking</b> — status timeline</sub></td>
<td><img src="Photos%20for%20Readme/Screenshot%202026-06-27%20093123.png" alt="Live map"><br><sub><b>Live map</b> — Leaflet route visualization</sub></td>
</tr>
</table>

### Administration

<p align="center">
<img src="Photos%20for%20Readme/Screenshot%202026-06-27%20092905.png" alt="Admin data management" width="900">
<br>
<sub><b>Data management</b> — grouped admin hubs for orders, partners, payments, and more</sub>
</p>

> **Demo GIF / partner & rider dashboards** — placeholders for future recordings. Partner and rider UIs are implemented under `/partners/` and `/riders/`.

---

## Roadmap

| Status | Item |
|--------|------|
| ✅ Current | Multi-role auth, restaurant catalog, cart/checkout, payments UI, order tracking, partner/rider registration, custom admin, REST API, email templates, PostHog hooks |
| 🔄 In progress | Expanded test coverage, CI/CD pipeline, production deployment hardening |
| 📋 Planned | Docker Compose, Redis caching in production, comprehensive API documentation (OpenAPI) |
| 🔮 Future | Mobile client (API-driven), push notifications, cloud media storage (S3-compatible), advanced rider GPS, automated dispatch |

---

## Contributing

We welcome structured contributions from team members and approved collaborators.

### Branch naming

```text
feature/<app>-<short-description>    # new functionality
fix/<app>-<short-description>        # bug fixes
docs/<topic>                         # documentation only
chore/<topic>                        # tooling, deps
```

### Pull request rules

1. Branch from latest `main`.
2. Keep PRs focused on **one subsystem** where possible.
3. Use the [commit convention](#commit-convention).
4. Request review from the **folder owner** and their designated reviewer.
5. Only **SwiftTe** merges to `main`.
6. One open **migration PR** at a time across the repository.
7. Do not include secrets, `.env` files, or local databases.

### Code review

- Subsystem owner reviews functional correctness.
- Reviewer checks integration impact and style.
- SwiftTe approves architectural, security, and migration changes.

---

## Repository ownership

### SwiftTe — Project lead

**Email:** `masterg578585@gmail.com` · 

| Owns | Examples |
|------|----------|
| Platform & architecture | `quickbite/settings/`, `manage.py`, root `urls.py` |
| Authentication & users | `users/`, `accounts/` |
| API | `api/` |
| Payments (gateway logic) | `payments/` services, eSewa/Khalti integration |
| Analytics | `analytics/`, PostHog middleware |
| Security & admin core | `core/admin_site.py`, `admin_registry.py`, `admin_analytics.py` |
| Deployment & CI | Gunicorn, production settings, future `.github/` workflows |

**Reviews:** Kdlskd (platform docs), Anupthapa25 (API consumers)

---

### Kdlskd — Operations & documentation

**Email:** `monilramjali5@gmail.com` · 

| Owns | Examples |
|------|----------|
| Partners | `partners/` — models, views, templates |
| Riders | `riders/` — models, views, templates |
| Email templates | `templates/emails/` |
| Documentation | `README.md`, `Documentation/`, `quickbite/docs/` |
| Testing | App-level and integration tests for operations domain |
| Admin UX (operations) | Partner/rider admin improvements |

**Reviews:** Anupthapa25 (UI), SwiftTe (security, migrations)

---

### Anupthapa25 — Customer experience

**Email:** `tanup7979@gmail.com` · 

| Owns | Examples |
|------|----------|
| Restaurants | `restaurant/` — views, services, menu |
| Orders | `orders/` — cart, checkout, tracking |
| Customer templates | `core/templates/orders/`, `restaurants/`, `profile/`, `components/` |
| Frontend assets | `core/static/css/`, customer-facing `js/`, images |
| Reviews & favorites UI | Customer-facing flows on restaurant models |

**Reviews:** SwiftTe (architecture), Kdlskd (partner order integration)

---

## Git workflow

```text
main (protected)
 ├── feature/platform-*     → SwiftTe
 ├── feature/customer-*     → Anupthapa25
 └── feature/ops-*          → Kdlskd
```

| Activity | Owner |
|----------|-------|
| Create feature branch | Subsystem author |
| Open pull request | Branch author |
| Review | Designated reviewer (see ownership) |
| Merge to `main` | **SwiftTe only** |
| Conflict resolution | Author + SwiftTe for shared files |
| Releases & tags | SwiftTe |
| Deployment | SwiftTe |
| Documentation releases | Kdlskd (content), SwiftTe (merge) |

---

## Commit convention

We follow [Conventional Commits](https://www.conventionalcommits.org/).

```text
<type>(<scope>): <description>
```

| Type | Usage |
|------|-------|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code change without behavior change |
| `docs` | Documentation only |
| `style` | CSS / formatting |
| `test` | Tests |
| `chore` | Tooling, dependencies |
| `perf` | Performance improvement |
| `ci` | CI/CD changes |

**Scopes:** `users`, `accounts`, `core`, `restaurant`, `orders`, `payments`, `partners`, `riders`, `api`, `analytics`, `ui`, `deploy`

**Examples:**

```text
feat(orders): add checkout coupon validation
fix(partners): validate PAN on registration
docs(readme): add installation guide for PostgreSQL
style(ui): improve mobile navbar layout
test(orders): cover order cancellation flow
feat(api): expose favorites endpoint
chore(deps): pin Django REST framework version
```

**Author emails (required for accurate contribution tracking):**

| Contributor | Email |
|-------------|-------|
| SwiftTe | `masterg578585@gmail.com` |
| Kdlskd | `monilramjali5@gmail.com` |
| Anupthapa25 | `tanup7979@gmail.com` |

---

## Development guidelines

| Topic | Guideline |
|-------|-----------|
| **Coding standards** | Follow PEP 8; match existing Django patterns in each app |
| **Naming** | `snake_case` for Python; descriptive URL names; app-prefixed template paths |
| **Folder ownership** | Commit only in your primary folders (see [Repository ownership](#repository-ownership)) |
| **Migrations** | One migration PR at a time; SwiftTe merges cross-app migrations |
| **Testing** | Add tests with feature PRs; run `python manage.py test` before requesting review |
| **Documentation** | Update README or `quickbite/docs/` when behavior changes |
| **Secrets** | Never commit `.env`, API keys, or database dumps |
| **Static assets** | Customer CSS/JS → Anupthapa25; admin JS → SwiftTe |

---

## License

Educational project developed for academic purposes.

**All rights reserved** unless otherwise specified by the institution or project supervisors.

---

## Authors

| Name | Role | GitHub |
|------|------|--------|
| **SwiftTe** | Project lead · platform, API, payments, security | [@SwiftTe](https://github.com/SwiftTe) |
| **Kdlskd** | Operations · partners, riders, documentation | [@Kdlskd](https://github.com/Kdlskd) |
| **Anupthapa25** | Customer experience · restaurants, orders, UI | [@Anupthapa25](https://github.com/Anupthapa25) |

**Organization:** [Bachelor-Of-Computer-Application](https://github.com/Bachelor-Of-Computer-Application)

**Repository:** [Bachelor-Of-Computer-Application/Alpha_Devs](https://github.com/Bachelor-Of-Computer-Application/Alpha_Devs)

---

## Acknowledgements

- [Django](https://www.djangoproject.com/) — web framework
- [Django REST Framework](https://www.django-rest-framework.org/) — API toolkit
- [SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/) — JWT authentication
- [Bootstrap](https://getbootstrap.com/) — UI components
- [Leaflet](https://leafletjs.com/) & [OpenStreetMap](https://www.openstreetmap.org/) — order tracking maps
- [PostHog](https://posthog.com/) — product analytics (optional integration)
- [eSewa](https://esewa.com.np/) & [Khalti](https://khalti.com/) — Nepal payment ecosystems
- Open-source Python community and Django documentation contributors

---

## Project status

| Attribute | Value |
|-----------|-------|
| **Phase** | Active development (beta) |
| **Context** | Academic group project — BCA |
| **Maintenance** | Actively maintained by core team |
| **Production** | Local/staging ready; production deployment planned |
| **Last updated** | June 2026 |

---

<div align="center">

**QuickBite Nepal** · Built with Django · Pokhara, Nepal

`main` · [Repository](https://github.com/Bachelor-Of-Computer-Application/Alpha_Devs) · Maintainers: SwiftTe · Kdlskd · Anupthapa25

</div>
