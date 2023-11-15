# syntax=docker/dockerfile:1

ARG IMAGE=3.11

FROM ${IMAGE}
ENV IPYTHONDIR=/nodeps/src/nodeps/ipython PYTHONPATH=/nodeps/src
ENV PYTHONSTARTUP=/nodeps/src/nodeps/ipython/profile_default/python_startup.py
COPY . /nodeps
WORKDIR /nodeps
VOLUME /nodeps
RUN pip install --upgrade -q pip && \
  pip install -q --no-cache-dir .[full]
