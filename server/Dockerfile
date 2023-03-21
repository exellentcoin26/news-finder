FROM python:3

COPY ./server /app

COPY ./db/schema.prisma /app

WORKDIR /app

RUN pip3 install .

RUN prisma generate --generator server

EXPOSE 5000

CMD python3 news_finder/main.py
