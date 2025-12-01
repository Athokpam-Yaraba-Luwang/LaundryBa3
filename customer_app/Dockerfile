FROM python:3.9-slim

WORKDIR /app

# Copy agents first (shared dependency)
COPY agents /app/agents

# Copy app
COPY customer_app /app/customer_app

# Install dependencies
RUN pip install flask gunicorn google-generativeai

WORKDIR /app/customer_app

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "wsgi:app"]
