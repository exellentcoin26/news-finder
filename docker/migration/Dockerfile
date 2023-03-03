FROM python:3

COPY ./db /app/db

WORKDIR /app/db

RUN pip3 install prisma

CMD prisma migrate deploy
