FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install uv && uv pip install --system fastapi uvicorn langgraph langchain langchain-openai openai python-dotenv httpx

COPY . .

EXPOSE 8003

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
