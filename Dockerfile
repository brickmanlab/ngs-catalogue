ARG PYTHON_VERSION="3.10-slim"

# Pre-build requirements
FROM python:${PYTHON_VERSION} as builder
ENV PYTHONUNBUFFERED 1
WORKDIR /app/

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY ./requirements.txt /app/requirements.txt
RUN pip install -Ur requirements.txt

# Initialize and run catalogue
FROM python:${PYTHON_VERSION} as runner
WORKDIR /app/

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ./src/* /app/

CMD ["panel", "serve", "database_browser_v1.py", "--address", "0.0.0.0", "--port", "5006", "--allow-websocket-origin", "*"]
