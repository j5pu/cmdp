# syntax=docker/dockerfile:1

ARG IMAGE=3.11-nodeps-deps

#FROM ${IMAGE} as base
#ARG PY_VERSION
#COPY . /nodeps
#WORKDIR /nodeps
#RUN pip install --upgrade -q pip && \
#  pip install -q --no-cache-dir .[full]

FROM ${IMAGE}
#ARG PY_VERSION
#COPY --from=base /usr/local/lib/python${PY_VERSION}/site-packages /usr/local/lib/python${PY_VERSION}/site-packages
#COPY --from=base /usr/local/bin /usr/local/bin
#COPY . /nodeps
#WORKDIR /nodeps
