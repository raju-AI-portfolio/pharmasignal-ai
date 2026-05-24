FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install uv && uv pip install --system fastapi uvicorn chromadb openai python-dotenv langchain langchain-openai langchain-community pypdf httpx

COPY . .

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
