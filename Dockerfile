# Build stage
FROM python:3.11-slim

RUN apt-get update

RUN apt-get install -y wkhtmltopdf  

RUN ln -s /usr/bin/wkhtmltopdf /usr/local/bin/wkhtmltopdf

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN groupadd -g 1000 app_group

RUN useradd -g app_group --uid 1000 app_user

RUN chown -R app_user:app_group /app

USER app_user

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]