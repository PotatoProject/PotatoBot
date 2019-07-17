FROM python:3.6-alpine

# Set environment varibles
ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client zlib-dev jpeg-dev libwebp-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libffi-dev libc-dev linux-headers postgresql-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

# Setup directory structure
RUN mkdir /app
WORKDIR /app
COPY . /app

## Add the wait script to the image
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.5.1/wait /wait
RUN chmod +x /wait

# Create user for execution
RUN adduser -D user
RUN chmod +x /app/entrypoint.sh && chown user:user /app
USER user

ENTRYPOINT ["sh", "entrypoint.sh"]
