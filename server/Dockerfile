FROM python:3

COPY ./server /app

COPY ./db/schema.prisma /app

WORKDIR /app

RUN pip3 install -r requirements.txt

RUN prisma generate

EXPOSE 5000

CMD python3 src/main.py
