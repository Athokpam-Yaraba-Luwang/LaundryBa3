FROM python:3.9-slim

WORKDIR /app

# Copy agents first (shared dependency)
COPY agents /app/agents

# Copy app
COPY business_app /app/business_app

# Install dependencies
# Note: We need to merge requirements or install separately.
# For simplicity, we'll install common ones.
RUN pip install flask gunicorn google-generativeai

WORKDIR /app/business_app

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "wsgi:app"]
