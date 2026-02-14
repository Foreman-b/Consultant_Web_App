# Consultant Booking Web Application

A role-based Django web application that allows clients to book sessions with a consultant.  
The platform supports authentication, structured booking management, and role-controlled dashboards for both clients and consultants.

---

## Project Overview

This system is designed as a single-consultant booking platform where:

- Users register as **clients** by default  
- Admin assigns **consultant** role  
- Clients can book sessions with a reason for consultation  
- Consultant reviews bookings, confirms status, and provides a meeting link  
- Both users access dedicated dashboards  

The application follows Django’s MVT architecture and enforces clean role-based access control.

---

## Architecture

### Backend Stack
- Python 3.13  
- Django  
- SQLite (development)  
- Django Authentication System  
- Custom User Model (extends `AbstractUser`)  

### Design Pattern
- MVT (Model–View–Template)  
- Role-Based Access Control (RBAC)  
- Server-side validation  
- Secure foreign key handling  

---

## User Roles

### Client
- Register and authenticate  
- Access booking dashboard  
- Book a session  
- Provide reason for booking  
- Track booking status  

### Consultant
- Access consultant dashboard  
- View who booked sessions  
- See reason for booking  
- Confirm or update booking status  
- Provide meeting link after confirmation  

Role escalation is strictly controlled by the admin.

---

## Database Models

- **User** (Custom model with role system)  
- **Booking**  
- (Optional) ConsultantProfile  

### Key Relationships
- Booking → linked to Client (User)  
- Booking → contains reason for session  
- Booking → contains status (Pending / Confirmed / Cancelled)  
- Booking → stores meeting link (added by consultant)  

---

## Features Implemented

- Environment configuration  
- Custom user authentication system  
- Booking form with validation  
- Client booking dashboard  
- Consultant booking management dashboard  
- Status confirmation workflow  
- Meeting link assignment system  

---

## Security Design

- Default role: CLIENT  
- Role field not exposed during registration  
- Foreign keys assigned server-side  
- Login required for protected routes  
- CSRF protection enabled  
- Secure authentication flow  

---

## Development Status

✔ Environment setup completed  
✔ Models implemented  
✔ Forms implemented  
✔ Authentication system completed  
✔ Client booking workflow completed  
✔ Consultant dashboard completed  
