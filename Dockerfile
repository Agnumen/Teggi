FROM python:3.13-alpine

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock* ./

RUN uv sync

COPY . .

CMD ["uv", "run", "python", "main.py"]
