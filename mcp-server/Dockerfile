FROM mcr.microsoft.com/playwright:v1.60.0-jammy

WORKDIR /app

RUN npm install -g @playwright/mcp@latest

EXPOSE 8931

CMD ["npx", "@playwright/mcp@latest", "--port", "8931", "--host", "0.0.0.0", "--browser", "chromium"]