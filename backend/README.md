# EatIt - Restaurant Order Management System

A web application supporting client, waiter, and kitchen workflows in a restaurant environment. The system allows placing and managing orders, controlling item availability, and managing users.

---

## 📦 Tech Stack
- **Backend**: Django + Django REST Framework
- **Database**: PostgreSQL (Dockerized)
- **Authentication**: JWT (SimpleJWT)
- **Documentation**: Swagger (drf-yasg)
- **UI**: planned frontend (React/HTML)

---

## 🧶 Local Setup

### 1. Run with Docker Compose

```bash
docker-compose up --build
```

Django Server: `http://localhost:8000`

Adminer (DB GUI): `http://localhost:8085`

---

## 🚪 REST API Endpoints

| Endpoint                            | Description                                  | Access Level        |
|-------------------------------------|----------------------------------------------|---------------------|
| `POST /api/users/register/`        | Register a new user                          | Public              |
| `GET /api/users/me/`               | Get current authenticated user              | Authenticated       |
| `GET /api/users/`                  | List all users                              | Manager only        |
| `PATCH /api/users/<id>/`           | Update user details                         | Manager only        |
| `GET /api/menu/items/`             | List all menu items                         | Everyone            |
| `POST /api/menu/items/`            | Add a new menu item                         | Manager only        |
| `PATCH/DELETE /items/<id>/`       | Update/Delete a menu item                   | Manager only        |
| `POST /menu/items/<id>/toggle-availability/` | Toggle item availability           | Manager or Kitchen  |
| `GET /api/orders/`                 | List orders based on user role              | Varies              |
| `POST /api/orders/`                | Create a new order                          | Client/Waiter       |
| `PATCH /api/orders/<id>/`          | Change order status                         | Manager only        |
| `GET /api/orders/<id>/history/`    | Get status change history for an order     | Manager/Waiter      |
| `GET /api/orders/stats/`           | Order statistics by status                  | Authenticated       |
| `GET /api/orders/manager/`         | All orders                                  | Manager             |
| `GET /api/orders/kitchen/`         | Orders to prepare (kitchen)                 | Kitchen             |
| `GET /api/orders/waiter/`          | Orders ready to serve (waiter)              | Waiter              |
| `GET /api/orders/<id>/`            | Retrieve a single order                     | Authenticated + Permissions |
| `GET /api/orders/<id>/history/`    | List status history for an order           | Authenticated       |

---

## 🔒 User Roles

- `client` – end-user placing an order
- `waiter` – waiter (can place orders on behalf of clients)
- `kitchen` – kitchen staff (handles order preparation)
- `manager` – system administrator with full control

---

## 📘 API Documentation
- Swagger UI: [`/swagger/`](http://localhost:8000/swagger/)
- Redoc: [`/redoc/`](http://localhost:8000/redoc/)

---

## ✅ Feature Checklist

- [x] JWT Authentication + role system
- [x] Menu item CRUD + image support
- [x] Order management + status transitions + status history
- [x] Role-based views (manager, waiter, kitchen)
- [x] Order statistics
- [x] Swagger API docs
- [x] Throttling + rate limiting
- [x] Audit logging to file + model
- [x] Filter orders by status and created_at
- [x] Toggle item availability (manager/kitchen)
- [x] Unittest coverage for users, menu, orders
- [x] Logging of user actions in critical endpoints
- [x] Endpoint for order status history
- [x] Extended API documentation
- [ ] Frontend (upcoming)

---

## 📂 Project Structure

```
backend/
├── api/
│   ├── menu/
│   ├── orders/
│   ├── users/
│   └── urls.py
├── core/            # custom User model + models
├── media/           # uploaded images
├── logs/            # audit logs
├── manage.py
├── settings.py
└── swagger_urls.py
```

---

## 🛠️ Authors & Contact
> For questions, issues, or collaboration opportunities — feel free to reach out to the project maintainer 😊
> kontakt.hayq@gmail.com
