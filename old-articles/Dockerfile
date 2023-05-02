FROM python:3

COPY ./old-articles /app

COPY ./db/schema.prisma /app

WORKDIR /app

RUN pip3 install .

RUN prisma generate --generator python

CMD python3 similarity_checker/main.py
