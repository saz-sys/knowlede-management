# syntax=docker/dockerfile:1
FROM node:20-alpine AS base

ENV PNPM_HOME="/pnpm" \
    PATH="$PNPM_HOME:$PATH" \
    NEXT_TELEMETRY_DISABLED=1

RUN apk add --no-cache bash git openssh && \
    corepack enable

WORKDIR /app

COPY package.json package-lock.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
