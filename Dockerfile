FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt ./
RUN pip install --user --no-cache-dir -r requirements.txt

COPY ./config.toml ./config.toml
COPY ./src ./src

CMD ["python", "src/main_server.py"]