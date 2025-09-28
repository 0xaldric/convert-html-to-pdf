FROM python:3.11-slim

# Install WeasyPrint dependencies
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libffi-dev \
    shared-mime-info \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN groupadd -g 1000 app_group

RUN useradd -g app_group --uid 1000 app_user

RUN chown -R app_user:app_group /app

USER app_user

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6000"]
