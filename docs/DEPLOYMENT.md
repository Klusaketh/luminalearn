# Deploying LuminaLearn AI

This puts the whole app online at a public address, free of charge, using four services:

| Service | What it does | Free plan limits |
| :--- | :--- | :--- |
| **Render** | Runs the website and API as one service | Sleeps after 15 idle minutes and takes about a minute to wake. 0.1 CPU, 512 MB memory. 750 hours a month, enough to run one service all month. |
| **Neon** | Stores accounts and lessons | 1 GB of storage and 100 compute hours a month. |
| **Brevo** | Sends verification and password reset emails | 300 emails a day. Render's free plan blocks normal email (SMTP) ports, so the app uses Brevo's API. |
| **Google AI Studio** | Provides the Gemini key behind the AI tutor | Depends on your key. |

Limits come from each provider's site and can change.

## How it runs

One container holds both servers. The Next.js server takes all public traffic and forwards `/api/v1` to the FastAPI backend, which is only reachable from inside the container. This is the same arrangement `npm run dev` uses (`scripts/start.mjs`). A single service means one wake-up instead of two and a single share of Render's 750 hours, and it has no second address to configure.

## Setup

### 1. Put the code on GitHub

Create an empty **private** repository at <https://github.com/new>, without a README. Keep it private: the project is marked proprietary and the repository includes your papers and reports.

From the project folder:

```bash
git add .dockerignore .env.example Dockerfile README.md render.yaml docs/DEPLOYMENT.md backend/app backend/requirements-prod.txt backend/tests/test_deployment.py scripts/start.mjs
git commit -m "Prepare production deployment on Render"
git remote add origin https://github.com/YOUR_USERNAME/luminalearn.git
git push -u origin perf-tutor-voice
```

`backend/.env` (your API key) and `backend/luminalearn.db` (your local accounts) are ignored by git and stay on your computer. The public site starts with no accounts.

### 2. Create the database on Neon

1. Create a project at <https://neon.com>. Choose the region **AWS US West 2 (Oregon)**, which matches `region` in `render.yaml`.
2. Open **Connect** and copy the connection string with **connection pooling turned off**. The host name must not contain `-pooler`; the app has been tested on direct connections only.

### 3. Set up email on Brevo

1. Create an account at <https://www.brevo.com>.
2. Under **Senders**, add the address emails should come from and confirm it with the 6-digit code Brevo sends you.
3. Under **SMTP & API > API keys**, create an API key.

### 4. Get a Gemini API key

Create a key at <https://aistudio.google.com/apikey>. Use a new key for this site, separate from your personal one, so you can replace it at any time.

Anyone who signs up spends this key's quota. A key from a project without billing gets rate limited rather than charged. Check Google's current terms before you choose: on the unpaid tier, Google may use what learners type to improve its products.

### 5. Deploy on Render

1. At <https://dashboard.render.com>, choose **New > Blueprint** and connect your GitHub repository.
2. Render reads `render.yaml` and asks for these values:

   | Setting | Value |
   | :--- | :--- |
   | `DATABASE_URL` | The Neon connection string from step 2 |
   | `GEMINI_API_KEY` | The key from step 4 |
   | `BREVO_API_KEY` | The key from step 3 |
   | `EMAILS_FROM_EMAIL` | The sender address you verified in step 3 |

   `SECRET_KEY` is generated for you.
3. Deploy. The first build takes several minutes. Your address appears at the top of the service page, such as `https://luminalearn.onrender.com`.

### 6. Check that it works

1. Open the site and sign up with a real email address.
2. Enter the code from the verification email (check spam).
3. Open a subject and a lesson. The curriculum loads just after the first start, so give it a minute if the list is empty.
4. Ask the AI tutor a question, and try the voice tutor.
5. Sign out, then use **Forgot password** and follow the emailed link.

## Updating the site

Commit and `git push` to the branch you deployed. Render rebuilds automatically, and changes in `content/` are synced after each start.

## If something goes wrong

Render's **Logs** tab shows the cause. The app stops at startup instead of running in an unsafe state.

| What you see | What to do |
| :--- | :--- |
| `Production needs SECRET_KEY...` | Set `SECRET_KEY` to a private random value of at least 32 characters. |
| `Production needs PostgreSQL...` | Set `DATABASE_URL`. |
| A connection error at startup | Copy the Neon connection string again and check the project is active. |
| Verification email never arrives | Look for `Brevo refused email` in the logs; it includes Brevo's reason, such as an unverified sender. A free email address such as Gmail can't be authenticated as a domain, so messages may land in spam; your own domain fixes this. |
| "Can't reach the LuminaLearn server" just after waking | The API is still starting. The page retries by itself. |
| Voice tutor refused on a custom domain | Set `FRONTEND_URL` to the address visitors use. |

## Optional additions

**Google sign-in.** Without it, the Google button tells visitors to use email and password. In Google Cloud, create an OAuth client of type *Web application* with your site's address as an authorized JavaScript origin. Then add the client ID on Render as both `GOOGLE_CLIENT_ID` and `NEXT_PUBLIC_GOOGLE_CLIENT_ID` and redeploy.

**No sleeping.** Changing the plan to Render's Starter instance ($7 a month at the time of writing) removes the wake-up delay and allows normal SMTP email.

**A different region.** Change `region` in `render.yaml` and pick the matching Neon region, such as Render `singapore` with Neon AWS Asia Pacific (Singapore), or Render `frankfurt` with Neon AWS Europe Central 1 (Frankfurt).

## Before promoting it widely

- **Sign-in and sign-up have no rate limit.** The AI endpoints do (`TUTOR_RATE_LIMIT_AUTHENTICATED`, set to 30 turns per learner per 10 minutes in `render.yaml`), but the limit is per learner, so many accounts can still use up the Gemini quota. Scripted sign-ups can also use up the daily email allowance.
- **Password hashing is slow on 0.1 CPU.** Each sign-in or sign-up uses about 0.4 CPU-seconds, so expect a pause of a few seconds, during which other requests wait. Heavy use needs a paid instance.
