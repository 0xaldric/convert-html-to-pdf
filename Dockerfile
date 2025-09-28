# Stage 1: get wkhtmltopdf
FROM surnet/alpine-wkhtmltopdf:3.12-0.12.6-full as wkhtml

# Stage 2: Python 3.11 app
FROM python:3.11-slim

# Copy wkhtmltopdf binary from Alpine stage
COPY --from=wkhtml /bin/wkhtmltopdf /usr/local/bin/wkhtmltopdf
COPY --from=wkhtml /bin/wkhtmltoimage /usr/local/bin/wkhtmltoimage

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN groupadd -g 1000 app_group

RUN useradd -g app_group --uid 1000 app_user

RUN chown -R app_user:app_group /app

USER app_user

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6000"]
