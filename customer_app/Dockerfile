FROM python:3.9-slim

WORKDIR /app

# Copy entire project to ensure shared libs (google, agents) are available
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app/customer_app

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "wsgi:app"]
