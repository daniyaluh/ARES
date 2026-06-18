# ARES

ARES is a Django marketplace for buying and selling robots and autonomous systems, ranging from consumer drones to military grade hardware. The platform layers identity verification, security clearances and export licensing on top of a standard e-commerce flow, so restricted or controlled products can only be purchased by users who meet the legal requirements.

## What it does

- Product catalog for robots and general products, with categories, variants, galleries, reviews and favorites
- Robot specific data such as AI capabilities, power systems and usage restrictions
- A verification system with clearance levels (public, confidential, secret, military, government, research and more)
- Export license applications and review for export controlled or military grade robots
- Purchase requests with an approval chain for restricted items, plus invoices, orders and seller payouts
- Support tickets, FAQs and technical manuals
- Two factor authentication with TOTP and WebAuthn security keys
- An analytics app for tracking platform activity

## Tech stack

- Python 3.13
- Django 6.0
- SQLite for local development
- Tailwind based templates rendered server side with Django's template engine

## Getting started

### Requirements

- Python 3.11 or newer
- pip

### Setup

Clone the repo and create a virtual environment.

```bash
git clone https://github.com/daniyaluh/ARES.git
cd ARES
python -m venv .venv
.venv\Scripts\activate   # on Windows
source .venv/bin/activate  # on macOS/Linux
```

Install dependencies.

```bash
pip install -r requirements.txt
```

Apply migrations.

```bash
python manage.py migrate
```

Create an admin account.

```bash
python manage.py createsuperuser
```

Run the dev server.

```bash
python manage.py runserver
```

The site will be available at `http://127.0.0.1:8000/` and the admin panel at `http://127.0.0.1:8000/admin/`.

## Configuration

The Django secret key is read from the `DJANGO_SECRET_KEY` environment variable, with a fallback for local development. Set it before deploying anywhere outside your own machine.

```bash
set DJANGO_SECRET_KEY=your-secret-key   # on Windows
export DJANGO_SECRET_KEY=your-secret-key  # on macOS/Linux
```

Emails are printed to the console by default since `EMAIL_BACKEND` is set to the console backend. Update `ares_project/settings.py` if you want to send real emails through SMTP.

## Project layout

- `users` - custom user model, profiles, roles, sessions, two factor auth and notifications
- `products` - products, robots, categories, specifications and reviews
- `verification` - clearance levels, verification requests, identity documents and export licenses
- `orders` - purchase requests, orders, invoices, transactions and seller payouts
- `support` - support tickets, FAQs and technical manuals
- `analytics` - platform usage and activity tracking

## Notes

This is a development build. `DEBUG` is enabled and the database is SQLite, so it is meant for local testing rather than production use as is.
