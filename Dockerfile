FROM python:3.11-bullseye

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

ENV NAME World

RUN python manage.py migrate && python manage.py add_test_users

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
