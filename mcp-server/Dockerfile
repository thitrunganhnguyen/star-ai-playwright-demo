FROM mcr.microsoft.com/playwright:v1.60.0-jammy

WORKDIR /app

RUN npm install -g @playwright/mcp@latest

RUN npx @playwright/mcp@latest install-browser chromium

COPY config.json /app/config.json

EXPOSE 8931

CMD ["npx", "@playwright/mcp@latest", "--config", "/app/config.json"]