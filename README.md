# Grey Academy

A Django project for Grey Academy — a tutor-led tech training hub (Frontend,
Backend, Cyber Security, Data Analysis tracks). Built as an authentication
practice project: custom user model, email verification with a 1-minute
expiring link, forgot-password flow, and Google sign-in.

---

## Features

- **Custom user model** — logs in with **email**, not username. Includes
  `phone_number`, `is_verified`, and `track` fields.
- **Signup** checks whether the email *or* phone number is already
  registered before creating the account, and rejects the request if so.
- **Email verification** — after signup, a verification link is emailed.
  The link expires **1 minute** after it's sent. The "check your inbox"
  page shows a live countdown ring and a **Resend** button that unlocks
  once the timer hits zero.
- **Login** blocks unverified accounts and sends them back to the
  verification page instead of letting them in.
- **Forgot password** always shows the same generic "if this account
  exists, we've sent a link" message — whether or not the email is
  actually registered. This is deliberate: it stops the form being used
  to check which emails have accounts (a common real-world security
  practice).
- **Google sign-in** via [django-allauth](https://docs.allauth.org/).
- Fully custom, hand-written templates + CSS (no frontend framework) —
  themed with colours sampled from the Greysoft logo, plus scroll-reveal
  and hover animations.

---

## Project structure

```
config/         Project settings, root urls.py
accounts/       Custom User model, signup/login/verify/reset views, forms
core/           Public site: home, about, courses, contact, dashboard
templates/      All HTML templates (base.html + accounts/ + core/)
static/         CSS, JS, logo images, hero video
```

---

## 1. Setup

```bash
# Clone / unzip the project, then from inside the project folder:
python -m venv env

# Windows
env\Scripts\activate
# macOS / Linux
source env/bin/activate

pip install -r requirements.txt

# Copy the example env file and fill in your own values
cp .env.example .env      # Windows: copy .env.example .env

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`.

> The `accounts.0002_set_local_site_domain` migration automatically points
> Django's Sites framework at `127.0.0.1:8000` so that email links (password
> reset, etc.) work correctly out of the box in development. **When you
> deploy to a real domain**, update this in `/admin/sites/site/` (or add
> another data migration) — otherwise your emails will link to the wrong
> place.

---

## 2. How email verification works (in development)

`EMAIL_BACKEND` defaults to Django's **console backend** — verification and
password-reset emails aren't actually sent anywhere; they're printed
straight to your terminal where `runserver` is running. Copy the link from
the terminal into your browser to verify an account or reset a password.

To send real emails, change `EMAIL_BACKEND` in `.env` to an SMTP backend
and fill in `EMAIL_HOST` / `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD`. Gmail,
SendGrid, Mailgun, etc. all work the same way — just different host/port.

---

## 3. Setting up Google Sign-In

Google login needs a **Client ID** and **Client Secret** from Google Cloud
Console. Takes about 5 minutes:

1. Go to **[Google Cloud Console](https://console.cloud.google.com/)** and
   create a new project (or pick an existing one).
2. In the left sidebar: **APIs & Services → OAuth consent screen**.
   - Choose **External** (unless you have a Google Workspace org).
   - Fill in the app name ("Grey Academy"), your email, and save through
     the steps. You can leave scopes/test users mostly default for dev.
3. Go to **APIs & Services → Credentials → Create Credentials → OAuth
   client ID**.
   - Application type: **Web application**.
   - **Authorized redirect URIs**, add:
     ```
     http://127.0.0.1:8000/accounts/google/login/callback/
     ```
     (and your real production URL later, e.g.
     `https://greyacademy.com/accounts/google/login/callback/`)
4. Click **Create** — Google shows you a **Client ID** and **Client
   Secret**. Copy both into your `.env`:
   ```
   GOOGLE_CLIENT_ID=your-client-id-here
   GOOGLE_CLIENT_SECRET=your-client-secret-here
   ```
5. Restart the server. The "Continue with Google" button on the login and
   signup pages will now work.

> While your OAuth consent screen is in **Testing** mode, only the Google
> accounts you explicitly add as "test users" (in the consent screen
> settings) can sign in. Publish the app (or add test users) as needed.

---

## 4. Auth flow summary

| Step | What happens |
|---|---|
| **Sign up** | `accounts/forms.py::SignUpForm` checks email + phone aren't already taken → account created with `is_verified=False` → 1-minute token generated → email sent → redirected to "check your inbox" |
| **Verify** | Clicking the emailed link (`accounts/verify-email/<token>/`) checks the token exists and hasn't expired → flips `is_verified=True` |
| **Resend** | Deletes the old token, issues a new one, restarts the countdown |
| **Log in** | If the account isn't verified yet, redirected back to the "check your inbox" page instead of logging in |
| **Forgot password** | Always shows the same generic confirmation message, regardless of whether the email is registered (see `accounts/forms.py::AcademyPasswordResetForm`) |
| **Google sign-in** | Handled entirely by `django-allauth` — see `/accounts/google/login/` |

---

## 5. Notes for extending this

- Course track data currently lives as a plain Python list in
  `core/views.py::COURSE_TRACKS`. Move it into a model if you want tutors
  to manage tracks from the Django admin.
- The contact form (`core/contact.html`) isn't wired to a backend yet —
  it's a static form. Add a view + a `Contact` model (or an email send) to
  make it functional.
- All CSS lives in `static/css/style.css`, organised into labelled
  sections (NAVBAR, HERO, AUTH PAGES, etc.) — search the ALL-CAPS headers
  to jump around quickly.
- Scroll animations are handled by `static/js/main.js` using
  `IntersectionObserver` — add `class="reveal"` to any element to have it
  fade/slide in in on scroll.

---

Built with Django 6.1, django-allauth, and plain CSS/JS — no frontend
framework required.
