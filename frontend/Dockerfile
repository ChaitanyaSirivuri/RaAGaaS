FROM oven/bun:1.1

WORKDIR /app

ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

COPY . .
RUN bun run build

EXPOSE 3000

CMD ["bun", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]
