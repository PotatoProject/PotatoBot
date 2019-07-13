FROM python:3.6-alpine

# Set environment varibles
ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache postgresql-client zlib-dev jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libffi-dev libc-dev linux-headers postgresql-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

# Setup directory structure
RUN mkdir /app
WORKDIR /app
COPY . /app
RUN chmod +x /app/entrypoint.sh

# Create user for execution
RUN adduser -D user
USER user

ENTRYPOINT ["sh", "entrypoint.sh"]