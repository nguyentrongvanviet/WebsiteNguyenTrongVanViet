# Deploy Django to Vercel (serverless)

This repo is a Django project. Vercel can run it as a **Python Serverless Function** via `api/index.py`.

## 1) Prereqs

- Put the project on GitHub (or GitLab/Bitbucket) so Vercel can import it.
- Create a PostgreSQL database (e.g. Neon/Supabase/Render). Copy its `DATABASE_URL`.

## 2) Vercel project settings

1. In Vercel: **New Project** → import your repo.
2. Framework preset: can stay **Other**.
3. Ensure install command uses your `requirements.txt` (default is fine).
4. Set **Build Command** to:

   `python manage.py collectstatic --noinput`

   (This generates `staticfiles/` for WhiteNoise.)

## 3) Environment variables (Vercel → Project → Settings → Environment Variables)

Required:
- `DJANGO_SECRET_KEY` = a long random secret
- `DATABASE_URL` = your Postgres connection string

Recommended:
- `DJANGO_DEBUG` = `False`
- `DJANGO_ALLOWED_HOSTS` = `.vercel.app`

Notes:
- `VERCEL` is automatically set by Vercel.
- The settings enable `CSRF_TRUSTED_ORIGINS = https://*.vercel.app` when running on Vercel.

## 4) Database migrations

Vercel doesn’t provide an interactive shell for running `manage.py migrate` as part of requests.
Run migrations from your computer (or CI) against the production database:

Windows (PowerShell):
- `$env:DATABASE_URL = "<your database url>"`
- `python manage.py migrate`

Windows (cmd):
- `set "DATABASE_URL=<your database url>"`
- `python manage.py migrate`

Note: many Postgres URLs include `&` parameters (e.g. `...sslmode=require&...`). In `cmd`, use the quoted form above (or escape `&` as `^&`) so it doesn’t get treated as a command separator.

## 5) Deploy

- Push to `main` (or your default branch). Vercel will build & deploy.
- Visit `https://<your-project>.vercel.app/HomeScreen/Welcome/`

## Limitations / gotchas

- Serverless functions are short-lived: no long-running processes.
- If you later add file uploads (`MEDIA_ROOT`), you’ll need external storage (S3/etc.).
