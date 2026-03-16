FROM python:3.11-slim

# Install Playwright/Chromium system dependencies
RUN apt-get update && apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    fonts-noto-cjk \
    fonts-liberation \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

# Install Chromium to a shared path accessible by all users
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers
RUN playwright install chromium

COPY . .

RUN groupadd -g 1000 app_group

RUN useradd -g app_group --uid 1000 app_user

RUN chown -R app_user:app_group /app

USER app_user

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6000"]
