# Omnigent on Hugging Face Spaces

> **Demo-grade target.** On the free tier, Space storage is **ephemeral** —
> data (and the SQLite DB) reset on restart. Good for kicking the tires, not for
> keeping state. For persistence, add HF's paid persistent-storage, or point
> `DATABASE_URL` at an external Postgres.

HF Spaces (Docker SDK) builds a Dockerfile at the Space repo root and runs it.
The shim here just pulls the prebuilt image. **No external database needed** —
the server runs on a SQLite file (a first-class backend), so a demo Space is two
files plus two secrets.

## Setup

1. Create a **Docker** Space on Hugging Face.
2. Add these two files at the Space repo root:
   - the `Dockerfile` from this directory (pulls the image), and
   - a `README.md` starting with this front-matter (HF reads it):
     ```yaml
     ---
     title: Omnigent
     emoji: 🤖
     colorFrom: indigo
     colorTo: blue
     sdk: docker
     app_port: 8000
     ---
     ```
3. In the Space **Settings -> Variables and secrets**, set:

   | Name | Kind | Value |
   |---|---|---|
   | `PORT` | variable | `8000` (pin it so the app and `app_port` agree) |
   | `HOST` | variable | `0.0.0.0` |
   | `DATABASE_URL` | variable | `sqlite:////data/artifacts/chat.db` |
   | `OMNIGENT_ACCOUNTS_COOKIE_SECRET` | secret | `openssl rand -hex 32` (pin it: ephemeral disk would otherwise drop sessions on restart) |

4. The Space builds + boots. Admin password is in the Space **Logs** on first
   boot. The base URL is auto-detected from `SPACE_HOST`, so it needs no manual
   set.
5. **Log in via the direct URL** `https://<user>-<space>.hf.space` in its own
   tab — not HF's embedded preview. The session cookie is `SameSite=Lax`, which
   browsers won't send inside HF's cross-origin iframe, so logging in from the
   embedded view loops back to `/login`. The direct URL is top-level
   (same-site), so login sticks. Make the Space **Public** so the direct URL
   isn't gated.

## Want persistence / multi-user later?

SQLite on a free Space is ephemeral (resets on restart). For data that survives,
swap `DATABASE_URL` for an **owned** external Postgres — the fastest is Neon:

1. Go to [pg.new](https://pg.new) and create a free Postgres. **Sign in to keep
   it** — an unclaimed instant database is throwaway and expires.
2. Copy the connection string and set it as the `DATABASE_URL` Space secret
   (replacing the SQLite value). The entrypoint normalizes `postgres://`
   automatically; the pooled or direct connection string both work.

That makes data survive restarts and supports more than one instance. Note the
**first boot takes ~1 minute** while migrations run against the remote database
(subsequent boots are fast), so don't be alarmed if the Space sits in "Building
/ Starting" for a bit.
