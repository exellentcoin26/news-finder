FROM rust:1.68

COPY ./rss-scraper /app/rss-scraper

COPY ./db/schema.prisma /app/db/schema.prisma

WORKDIR /app/rss-scraper

# Not needed in the future when the rust prisma cli supports specifying generator
RUN apt-get update && apt-get install -y python3-pip

RUN pip3 install prisma

RUN prisma generate --generator rss-scraper --schema ../db/schema.prisma

CMD cargo run --release
