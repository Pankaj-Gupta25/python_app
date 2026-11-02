# ── Build stage ────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Install dependencies into a virtual env so we can copy them cleanly
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# ── Runtime stage ───────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy the pre-built virtual env from the builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source
COPY . .

# Neon DB connection string must be injected at runtime via --env / --env-file
# Do NOT bake secrets into the image.
ENV DATABASE_URL=""

EXPOSE 8000

# Run with a single uvicorn worker; scale horizontally via container replicas.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
