FROM python:3.12.6-alpine3.20

WORKDIR /usr/src/app

COPY req.txt req.txt
RUN apk update && \
    apk add postgresql-dev
RUN pip install --no-cache-dir psycopg2-binary
RUN pip install --no-cache-dir -r req.txt

COPY . .


CMD ["python", "bot.py"]