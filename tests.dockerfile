# syntax=docker/dockerfile:1

# https://medium.com/@harishpillai1994/how-to-run-pytest-in-docker-container-and-publish-the-results-in-allure-reporting-a96499f28f9f
# https://xnuinside.medium.com/integration-testing-for-bunch-of-services-with-pytest-docker-compose-4892668f9cba
ARG PY_VERSION=3.11
FROM python:${PY_VERSION}-slim

ENV PIP_ROOT_USER_ACTION=ignore PYTHONPATH=/nodeps/src

RUN apt-get update && \
  apt-get install --no-install-recommends -y git openssh-client && \
  rm -rf /var/cache/apt/archives  && ln -sf /bin/bash /bin/sh && \
  mkdir -p -m 0600 ~/.ssh && \
  ssh-keyscan -H github.com bitbucket.org >> ~/.ssh/known_hosts

COPY . /nodeps
WORKDIR /nodeps
VOLUME /nodeps

RUN pip install --upgrade -q pip && \
  pip install -q --no-cache-dir . .[full]
