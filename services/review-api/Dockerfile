FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install uv && uv pip install --system fastapi uvicorn psycopg2-binary sqlalchemy python-dotenv

COPY . .

EXPOSE 8004

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
