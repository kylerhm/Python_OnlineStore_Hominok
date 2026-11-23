FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

RUN python manage.py makemigrations store users
RUN python manage.py migrate
RUN python manage.py collectstatic --no-input

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
