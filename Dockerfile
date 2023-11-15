# syntax=docker/dockerfile:1

ARG PY_VERSION=3.11
FROM j5pu/${PY_VERSION}
ENV IPYTHONDIR=/usr/local/lib/python${PY_VERSION}/site-packages/nodeps/ipython
ENV PYTHONSTARTUP=/usr/local/lib/python${PY_VERSION}/site-packages/nodeps/ipython/profile_default/python_startup.py
ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install --upgrade -q pip && pip install -q --no-cache-dir nodeps[full]