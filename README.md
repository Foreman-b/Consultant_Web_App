## Consultant Booking Web Application
Full-Stack Production Documentation

A robust, role-based Django platform enabling clients to discover consultants, book availability-based sessions, and provide feedback through a structured review system.


# 1. Project Overview
A professional marketplace platform designed to bridge the gap between expert consultants and clients. The application manages the entire lifecycle of a professional engagement: from availability scheduling and secure Paystack payments to virtual meeting hosting and peer reviews.

# 2. System Architecture
Technical Stack
Framework: Django 5.x (Python 3.13)

Database: PostgreSQL (Production grade, relational storage)

Frontend: Bootstrap 5 with custom "Dark Mode" CSS

Static Management: WhiteNoise (for serving files in production)

Payment Gateway: Paystack API (Secure NGN/USD transactions)

WSGI Server: Gunicorn

# 3. Core Database Models (The "Big Six")
The system logic is built around six primary pillars:

# 4. Key Workflows
A. Availability & Booking
Consultants use Inline Formsets to manage multiple dates simultaneously. Clients browse these slots and select a time. The system prevents overbooking by tracking max_slots per availability instance.

B. Payment Integration (Paystack)
The booking remains "Pending" until a successful Paystack transaction is recorded.

Initialize: Generate a unique reference and redirect to Paystack.

Verify: View-side logic confirms payment with Paystack's servers.

Confirm: Upon verification, the booking is activated, and the consultant is notified.

C. Post-Session Feedback
Reviews are locked behind a "Completion" gate. A client can only submit a ReviewForm (Rating 1-5 and Comments) if the Booking.status is marked as COMPLETED. This ensures all reviews are from verified, paying customers.

# 5. Security & Access Control
Role-Based Access (RBAC): Custom properties is_consultant and is_client protect views.

Lazy Referencing: Models use string references (e.g., 'Booking') to prevent circular import crashes during startup.

Identity Protection: Identity fields (client, consultant) are handled via commit=False in the backend to prevent users from manipulating POST data.

Environment Safety: All keys (Paystack Secret, Database URL) are stored in environment variables, never hardcoded.

# 6. Deployment & Environment Config
Required Environment Variables
To deploy on Render or Coolify, you must set these variables in the dashboard:

Production Setup
Media Files: Profile pictures are stored in MEDIA_ROOT.

Static Files: WhiteNoise handles CSS/JS delivery without the need for a separate Nginx server.

Database Migration: The transition from SQLite to PostgreSQL is handled via python manage.py migrate during the build step.

# 7. Development Status
✔ Authentication: Custom User, Roles, and Profile Pictures.

✔ Consultant Tools: Availability Management.

✔ Client Tools: Booking Dashboard and Session Selection.

✔ Financials: Paystack Payment Verification.

✔ Social: Verified Review and Rating System.