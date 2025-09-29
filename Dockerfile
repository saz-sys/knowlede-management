# syntax=docker/dockerfile:1
FROM node:20-alpine AS base

ENV PNPM_HOME="/pnpm" \
    PATH="$PNPM_HOME:$PATH" \
    NEXT_TELEMETRY_DISABLED=1

# 適当な箇所でbashをインストール
# alpine系
RUN apk add --no-cache bash git openssh curl && \
    corepack enable
# ubuntu系
# RUN apt-get update && apt-get install -y bash

WORKDIR /app

RUN npm install -g @aikidosec/safe-chain
RUN safe-chain setup

COPY package.json package-lock.json ./

RUN ["/bin/bash", "-c", "source ~/.bashrc && npm -v && npm ci"]

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
