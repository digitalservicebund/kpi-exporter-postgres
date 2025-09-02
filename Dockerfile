FROM python:3.13.6-alpine3.22

RUN apk update \
  && apk add --no-cache jq postgresql-client \
  && rm -rf /var/cache/apk/* \
  && pip install --no-cache-dir requests pyyaml

WORKDIR /app

COPY query_and_submit.py .

CMD ["python", "./query_and_submit.py"]
