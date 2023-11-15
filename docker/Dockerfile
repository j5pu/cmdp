# syntax=docker/dockerfile:1

ARG PY_VERSION=3.11

FROM python:${PY_VERSION}-slim as slim
ENV PIP_ROOT_USER_ACTION=ignore STARSHIP_CONFIG=/root/.starship.toml
ADD https://starship.rs/install.sh /tmp/install.sh
RUN apt-get update && \
    apt-get install --no-install-recommends -y git openssh-client wget && \
    rm -rf /var/cache/apt/archives  && ln -sf /bin/bash /bin/sh && \
    mkdir -p -m 0600 ~/.ssh && \
    ssh-keyscan -H github.com bitbucket.org >> ~/.ssh/known_hosts  && \
    chmod +x /tmp/install.sh && /tmp/install.sh --yes && rm /tmp/install.sh && \
    echo 'eval "$(starship init bash)"' >> /etc/bash.bashrc  && \
    printf "%s\n" "command_timeout = 4000" "[hostname]" "ssh_only = false" "disabled = false" > /root/.starship.toml

FROM python:${PY_VERSION}-alpine as alpine
ENV PIP_ROOT_USER_ACTION=ignore STARSHIP_CONFIG=/root/.starship.toml
RUN apk add  --no-cache bash git openssh-client starship && \
    mkdir -p -m 0600 ~/.ssh && \
    ssh-keyscan -H github.com bitbucket.org >> ~/.ssh/known_hosts  && \
    sed -i 's|^root.*|root:x:0:0:root:/root:/bin/bash|' /etc/passwd && \
    echo 'eval "$(starship init bash)"' >> /etc/bash/bashrc  && \
    printf "%s\n" "command_timeout = 4000" "[hostname]" "ssh_only = false" "disabled = false" > /root/.starship.toml

