#!/usr/bin/env bash
set -o errexit
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
```

**`Procfile`**
```
web: gunicorn facial_project.wsgi:application --bind 0.0.0.0:$PORT