# Django Production‑Ready Template 🚀

A simple and clean Django template ready for production. It includes Docker, PostgreSQL, Redis, Celery environment-based settings, and a few handy tools to get you started quickly.

---

# ⚡ Quick Start
### **Local Development (without Docker)**
1. #### **Create a virtual environment**
```bash
   python -m venv <prefered-env-name>
```
**But I recommend to use `.venv`**
```bash
python -m venv .venv
```
2. #### **Activate your environment**
**Using Windows**
```bash
.\<environment-name>\Scripts\activate.bat
```
**Using Linux**
```bash
source .<environment-name>/bin/activate
```
3. **Install the requirements**
```bash
pip install -r requirements/development.txt
```
4. **Run the app**
```bash
python manage.py runserver
```

### **Docker Setup**
1. #### **Clone the repository**
#### **Using HTTP**
   ```bash
   git clone https://github.com/ooplaza/Django-Production-Ready-Template.git
   cd Django-Production-Ready-Template
   ```
#### **Using SSH**
```bash
git clone git@github.com:<your-host-name>/Django-Production-Ready-Template.git
```

2. #### **Copy and edit your .env**
```bash
copy .env-example .env
```

3. #### **Run and build**
```bash
docker compose up --build
```

### **Executing Celery Beat and Worker**
```bash
docker exec -it templateapi celery -A config worker --beat --loglevel=info
```

## ✨ Features
- **Production-ready** configurations
- **Dockerized** (Django, PostgreSQL, Redis)
- **Django** 4.2+ with environment-based settings
- **Celery + Redis** ready for asynchronous tasks
- **Separate** `requirements` for development and production
- **JWT (cookie-based) authentication** using `JWTCookieAuthentication` from `dj-rest_auth`
- **OAuth2 authentication** for third-party apps via `django-oauth-toolkit`

## 📦 Dependencies
- **Python**: 3.11 or higher
- **Django**: 4.2 or higher
- **PostgreSQL**: 13 or higher
- **Docker** & **Docker Compose**
