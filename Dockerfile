# syntax=docker/dockerfile:1

# https://medium.com/@harishpillai1994/how-to-run-pytest-in-docker-container-and-publish-the-results-in-allure-reporting-a96499f28f9f
# https://xnuinside.medium.com/integration-testing-for-bunch-of-services-with-pytest-docker-compose-4892668f9cba
FROM python:3.11-slim-buster as builder

ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install --upgrade -q pip && pip install -q --no-cache-dir nodeps[full]