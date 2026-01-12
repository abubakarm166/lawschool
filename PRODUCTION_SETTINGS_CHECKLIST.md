# Production Settings Checklist

## Required Settings Updates for Production

### 1. Static Files Configuration ✅ (Fixed)
- `STATIC_ROOT` is now set to `staticfiles` directory
- `STATICFILES_DIRS` points to your source static files
- Run `python manage.py collectstatic` to collect all static files

### 2. Debug Mode ✅ (Fixed)
- `DEBUG = False` for production (security)

### 3. Allowed Hosts ⚠️ (Needs Update)
Update `ALLOWED_HOSTS` in `school/settings.py`:

```python
ALLOWED_HOSTS = ['your-domain.com', 'your-ip-address', 'localhost']
```

Example:
```python
ALLOWED_HOSTS = ['example.com', '172.31.19.135', 'localhost']
```

### 4. Site URL ⚠️ (Needs Update)
Update `SITE_URL` in `school/settings.py`:

```python
SITE_URL = 'http://your-domain-or-ip'
```

Example:
```python
SITE_URL = 'http://172.31.19.135'  # or your domain
```

### 5. Database Configuration
Make sure your database settings are correct for production.

### 6. Secret Key
Consider using environment variables for `SECRET_KEY` in production:
```python
import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-fallback-key')
```

## After Updating Settings

1. **Create staticfiles directory:**
```bash
mkdir -p /home/ubuntu/lawschool/staticfiles
```

2. **Collect static files:**
```bash
cd /home/ubuntu/lawschool
source env/bin/activate
python manage.py collectstatic --noinput
```

3. **Update nginx to serve from staticfiles:**
Make sure your nginx config points to the collected static files:
```nginx
location /static/ {
    alias /home/ubuntu/lawschool/staticfiles/;
}
```

4. **Restart services:**
```bash
sudo supervisorctl restart gunicorn
sudo service nginx restart
```
