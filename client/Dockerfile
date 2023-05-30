FROM node

COPY ./client /app

COPY ./docker/server-url.env /app/.env

WORKDIR /app

RUN npm install -g pnpm

RUN pnpm install

RUN pnpm run build

EXPOSE 8080

CMD npm run preview
