FROM node

COPY . /app

WORKDIR /app

EXPOSE 8080

RUN npm install

RUN npm run build

CMD npm run preview
