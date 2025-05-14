FROM ubuntu:24.04

USER root
ENV DEBIAN_FRONTEND=noninteractive
ENV TS=Etc/UTC
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

WORKDIR /root

RUN echo 'APT::Install-Suggests "0";' >> /etc/apt/apt.conf.d/00-docker
RUN echo 'APT::Install-Recommends "0";' >> /etc/apt/apt.conf.d/00-docker
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    tzdata \
    python3 \
    python3-pip \
    python3-venv && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv/ai-demo

COPY requirements.txt .
COPY src/ ai-demo/

RUN . "/opt/venv/ai-demo/bin/activate" && \
    python3 -m pip install -U pip setuptools && \
    python3 -m pip install -r requirements.txt

ENTRYPOINT ["/opt/venv/ai-demo/bin/python3", "-B", "ai-demo/main.py", "-p", "5555"]
