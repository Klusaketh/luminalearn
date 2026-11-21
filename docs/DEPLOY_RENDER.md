# Deploying LuminaLearn AI to Render

`render.yaml` at the repo root is a Render **Blueprint**: one file that describes every piece of
the production stack. Render reads it and creates:

| Resource | What it is | Built from |
| --- | --- | --- |
| `luminalearn-db` | PostgreSQL 16 database | managed by Render |
| `luminalearn-api` | FastAPI backend | `backend/Dockerfile` (context: repo root) |
| `luminalearn-web` | Next.js frontend | `frontend/Dockerfile` (context: `frontend/`) |

```
Browser ──► luminalearn-web ──/api/v1──► luminalearn-api ──► luminalearn-db
                                              └──► Gemini API, SMTP
```

The browser only talks to the frontend. The frontend's server forwards `/api/v1` to `BACKEND_URL`,
so no CORS setup is needed.

## Before you start: collect these

1. **Gemini API key**: <https://aistudio.google.com/apikey>
2. **SMTP login** (required: sign-up sends a verification code by email). With Gmail:
   - turn on 2-Step Verification in your Google Account
   - create an App Password: Google Account → Security → App passwords
   - use `SMTP_HOST=smtp.gmail.com`, `SMTP_USER=<you>@gmail.com`, `SMTP_PASSWORD=<16-char app password>`,
     `EMAILS_FROM_EMAIL=<you>@gmail.com`
3. *(Optional)* Google OAuth client ID and secret, for "Sign in with Google".

## Deploy (about 10 minutes, mostly waiting for builds)

1. Sign in at <https://dashboard.render.com> with GitHub.
2. **New → Blueprint**, choose the `luminalearn` repo and the `main` branch.
3. Render lists the three resources and asks for every `sync: false` value. Paste the values
   from above. Leave the Google fields empty if you aren't using Google sign-in.
4. Click **Apply**. The database is created first, then both services build.
5. When `luminalearn-api` is live, open its page and check its URL.
   - If it is exactly `https://luminalearn-api.onrender.com`, you're done.
   - If Render added a suffix (for example `luminalearn-api-x7k2.onrender.com`), open
     `luminalearn-web → Environment`, set `BACKEND_URL` to the real URL, then
     **Manual Deploy → Clear build cache & deploy**. The frontend must be *rebuilt*, because the voice
     WebSocket address is fixed at build time.
6. Open the `luminalearn-web` URL, register, and enter the code from your email.

## Checking it works

- `https://<api-url>/api/v1/health` returns `"status": "healthy"`
- Signed in, `https://<web-url>/api/v1/tutor/status` shows `"llm_enabled": true`. If it's `false`,
  `GEMINI_API_KEY` is missing or wrong, and the tutor falls back to its offline engine.
- Logs: each service's **Logs** tab. Lines starting with `[INIT] Syncing the LuminaLearn academic
  curriculum` show the course catalog being loaded on startup.

## Things to know

- **Free services sleep** after 15 minutes idle, so the first visit afterwards takes 30–60 seconds.
  The frontend can wake before the backend, and then shows "server is restarting" for a moment.
- **Free Postgres expires after 30 days.** Move it to a paid plan before then if you have real users.
- **Every push to `main` redeploys.** On every start the backend syncs `content/` into the database.
  The sync never deletes or renames anything (see `content/README.md`).
- **Google sign-in**: add the frontend URL to the OAuth client's Authorized JavaScript origins in
  Google Cloud Console.
