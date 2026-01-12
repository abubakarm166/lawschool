# Deployment Fix for 502 Bad Gateway Error

## Issue Analysis
The 502 Bad Gateway error typically occurs when nginx cannot communicate with gunicorn. Based on your configuration, here are the likely issues and fixes:

## Problem 1: Incorrect WSGI Path
Your supervisor config uses `core.wsgi:application` but your project is named `school`.

**Fix:** Update the gunicorn command in `/etc/supervisor/conf.d/gunicorn.conf`:

```ini
[program:gunicorn]
directory=/home/ubuntu/lawschool
command=/home/ubuntu/lawschool/env/bin/gunicorn --workers 3 --bind unix:/home/ubuntu/lawschool/app.sock --timeout 600 school.wsgi:application
autostart=true
autorestart=true
stderr_logfile=/home/ubuntu/lawschool/logs/gunicorn.err.log
stdout_logfile=/home/ubuntu/lawschool/logs/gunicorn.out.log
user=ubuntu
```

**Changes:**
- Changed `core.wsgi:application` to `school.wsgi:application`
- Fixed log file paths (added full path `/home/ubuntu/lawschool/logs/`)
- Added `user=ubuntu` to run as the correct user

## Problem 2: Log Directory Permissions
The logs directory needs proper permissions.

**Fix:**
```bash
sudo mkdir -p /home/ubuntu/lawschool/logs
sudo chown -R ubuntu:ubuntu /home/ubuntu/lawschool/logs
sudo chmod -R 755 /home/ubuntu/lawschool/logs
```

## Problem 3: Socket File Permissions
The socket file needs proper permissions for nginx to access it.

**Fix:**
```bash
sudo chown -R ubuntu:www-data /home/ubuntu/lawschool
sudo chmod -R 755 /home/ubuntu/lawschool
```

## Problem 4: Static Files Collection
Make sure static files are collected.

**Fix:**
```bash
cd /home/ubuntu/lawschool
source env/bin/activate
python manage.py collectstatic --noinput
```

## Problem 5: Environment Variables
Make sure Django settings are configured for production.

**Check in `/home/ubuntu/lawschool/school/settings.py`:**
- `DEBUG = False` (for production)
- `ALLOWED_HOSTS = ['your-domain.com', 'your-ip-address']`
- Database settings are correct
- Static files settings are correct

## Complete Deployment Checklist

### 1. Update Supervisor Configuration
```bash
sudo nano /etc/supervisor/conf.d/gunicorn.conf
```

Paste this corrected configuration:
```ini
[program:gunicorn]
directory=/home/ubuntu/lawschool
command=/home/ubuntu/lawschool/env/bin/gunicorn --workers 3 --bind unix:/home/ubuntu/lawschool/app.sock --timeout 600 school.wsgi:application
autostart=true
autorestart=true
stderr_logfile=/home/ubuntu/lawschool/logs/gunicorn.err.log
stdout_logfile=/home/ubuntu/lawschool/logs/gunicorn.out.log
user=ubuntu
environment=PATH="/home/ubuntu/lawschool/env/bin"
```

### 2. Create Logs Directory
```bash
sudo mkdir -p /home/ubuntu/lawschool/logs
sudo chown -R ubuntu:ubuntu /home/ubuntu/lawschool/logs
```

### 3. Set Permissions
```bash
sudo chown -R ubuntu:www-data /home/ubuntu/lawschool
sudo chmod -R 755 /home/ubuntu/lawschool
```

### 4. Update Nginx Configuration
Make sure your nginx config has the correct socket path:

```nginx
server {
    listen 80;
    server_name your-domain.com your-ip-address;
    
    location / {
        include proxy_params;
        proxy_read_timeout 300s;
        proxy_connect_timeout 120s;
        proxy_pass http://unix:/home/ubuntu/lawschool/app.sock;
    }
    
    location /static/ {
        autoindex on;
        alias /home/ubuntu/lawschool/static/;
    }
    
    location /media/ {
        autoindex on;
        alias /home/ubuntu/lawschool/media/;
    }
}
```

### 5. Collect Static Files
```bash
cd /home/ubuntu/lawschool
source env/bin/activate
python manage.py collectstatic --noinput
```

### 6. Update Django Settings for Production
In `/home/ubuntu/lawschool/school/settings.py`:

```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'your-ip-address', 'localhost']

# Add this for static files in production
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
```

### 7. Restart Services
```bash
# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart gunicorn

# Check status
sudo supervisorctl status

# Test nginx config
sudo nginx -t

# Restart nginx
sudo service nginx restart
```

### 8. Check Logs for Errors
```bash
# Check gunicorn logs
sudo cat /home/ubuntu/lawschool/logs/gunicorn.err.log
sudo cat /home/ubuntu/lawschool/logs/gunicorn.out.log

# Check nginx error log
sudo tail -f /var/log/nginx/error.log

# Check supervisor logs
sudo tail -f /var/log/supervisor/supervisord.log
```

## Common Issues and Solutions

### Issue: "No module named 'school'"
**Solution:** Make sure you're in the correct directory and the virtual environment is activated.

### Issue: Permission denied on socket
**Solution:** 
```bash
sudo chown ubuntu:www-data /home/ubuntu/lawschool/app.sock
sudo chmod 666 /home/ubuntu/lawschool/app.sock
```

### Issue: Static files not loading
**Solution:**
1. Run `python manage.py collectstatic`
2. Check nginx has read permissions on static directory
3. Verify STATIC_ROOT in settings.py

### Issue: Database errors
**Solution:**
1. Make sure database migrations are run: `python manage.py migrate`
2. Check database permissions
3. Verify database settings in settings.py

## Testing Steps

1. **Test gunicorn directly:**
```bash
cd /home/ubuntu/lawschool
source env/bin/activate
gunicorn school.wsgi:application --bind 0.0.0.0:8000
```
If this works, gunicorn is fine. Press Ctrl+C to stop.

2. **Check supervisor status:**
```bash
sudo supervisorctl status gunicorn
```
Should show "RUNNING"

3. **Check if socket file exists:**
```bash
ls -la /home/ubuntu/lawschool/app.sock
```

4. **Test nginx configuration:**
```bash
sudo nginx -t
```

## Final Verification

After all fixes, test your site:
```bash
curl http://localhost
```

If you get a response, nginx and gunicorn are communicating properly.
