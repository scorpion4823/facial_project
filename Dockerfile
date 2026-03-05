FROM animcogn/face_recognition:cpu

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --no-input

CMD ["sh", "-c", "gunicorn facial_project.wsgi:application --bind 0.0.0.0:${PORT:-8000} --timeout 120 --workers 1"]