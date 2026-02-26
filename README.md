# Consultant Booking Web Application

### Full-Stack Production Platform (Django & REST Framework)

**Live Production URL:** [https://consultant-web-app-production.up.railway.app](https://consultant-web-app-production.up.railway.app)

A robust, role-based marketplace enabling clients to discover consultants, book availability-based sessions via secure payments, and provide verified feedback.

---

## 1. Project Overview

This application manages the entire lifecycle of professional consulting engagements. It transitions from a traditional monolithic web app to an API-ready platform, handling everything from complex scheduling logic and **Paystack** financial verification to virtual meeting hosting and peer-reviewed ratings.

## 2. Technical Stack

* **Backend:** Django 5.x (Python 3.13)
* **API Layer:** Django REST Framework (DRF)
* **API Documentation:** Swagger UI / OpenAPI 3.0
* **Database:** PostgreSQL (Production-grade relational storage)
* **Frontend:** Bootstrap 5 (Custom Dark Mode) & SweetAlert2 (Dynamic Notifications)
* **Deployment:** Railway (PaaS) with Gunicorn & WhiteNoise

## 3. Core Database Architecture

The system logic is built around six primary pillars:

1. **CustomUser:** Extended `AbstractUser` featuring **TextChoices** for Roles (Client/Consultant) and specialized properties `is_consultant`/`is_client`.
2. **ConsultantProfile:** One-to-one relationship with User, storing professional bios and profile imagery.
3. **Availability:** Management of time-slots using Inline Formsets.
4. **Booking:** The central contract linking Client, Consultant, and Payment status.
5. **Payment:** Paystack - Sandbox/Test Mode
6. **Review:** A verified feedback system restricted to **COMPLETED** sessions only.

## 4. Key Workflows

### A. Availability & Booking

Consultants manage their schedule via a dedicated dashboard. Clients browse these slots in real-time. The system implements strict validation to prevent double-booking and tracks `max_slots` per availability instance.

### B. Secure Payment (Paystack)

Financial transactions are handled through the Paystack - Sandbox/Test Mode:

* **Initialize:** Generates a unique reference and redirects to the secure payment gateway.
* **Verify:** Backend logic confirms the success of the transaction with Paystack servers before activating the booking.
* **Fulfillment:** Once verified, the consultant provides the meeting link via the dashboard.

### C. Account Recovery (No-Email Reset)

To eliminate dependency on SMTP servers in production, the app uses a **Security Question** recovery system:

* Users choose a question and answer during **Registration**.
* The `CustomUser` model overrides the `save()` method to normalize (lowercase/strip) answers.
* The **Forgot Password** flow verifies the answer against the database to grant reset access instantly.

## 5. Security & UI Experience

* **RBAC:** Decorators and Mixins ensure users only access dashboards relevant to their role.
* **Real-time Feedback:** Integrated **SweetAlert2** with the Django Messages framework to provide "Toast" notifications for successful logins, payments, and password resets.
* **Environment Safety:** Sensitive credentials (DB URL, Paystack Keys, Secret Key) are managed strictly via environment variables.

## 6. API Access

The platform is fully "Headless" ready. Developers can interact with the system via the REST API.

* **Documentation:** Available at  (Django Rest Framework) `/api/client/`, `/api/consultant/` and (Swagger) `/api/docs/`, `/api/schema/`.
* **Endpoints:** Token-based access to Profiles, Bookings, and Availability lists.

## 7. Development Status & Features

* ✔ **Auth:** Custom User, Roles, and Profile Pictures.
* ✔ **Security:** Independent Security Question Reset system.
* ✔ **Consultant Tools:** Bulk Availability Management & Meeting Link Provision.
* ✔ **Client Tools:** Booking Dashboard & Star Rating Reviews.
* ✔ **Financials:** Paystack Payment Verification Integration.
* ✔ **API:** DRF Endpoints with Swagger UI auto-generation.

---

## 8. Local Setup & Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Foreman-b/Consultant_Web_App.git
cd Consultant_Web_App

```


2. **Create and activate virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

```


3. **Install dependencies:**
```bash
pip install -r requirements.txt

```


4. **Apply Migrations:**
```bash
python manage.py migrate

```


5. **Run Server:**
```bash
python manage.py runserver

```
