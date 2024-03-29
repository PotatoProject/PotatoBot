FROM python:3.9-slim as base

RUN pip install pipenv
COPY Pipfile* /tmp/

# Setup env
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER 1

FROM base AS python-deps

# Install pipenv and compilation dependencies
RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Install python dependencies in /.venv
COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

FROM base AS runtime

# Copy virtual env from python-deps stage
COPY --from=python-deps /.venv /.venv
ENV PATH="/.venv/bin:$PATH"

# install Pillow dependencies
RUN apt-get update && apt-get install -y --no-install-recommends libtiff5-dev libjpeg-dev libopenjp2-7-dev \
	zlib1g-dev liblcms2-dev libwebp-dev

# Create and switch to a new user
RUN useradd --create-home user
WORKDIR /home/user
USER user

# Install application into container
COPY . .

# Run the application
ENTRYPOINT ["python", "-m", "kang_bot"]
