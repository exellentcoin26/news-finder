# News finder

News aggregator application made for the `Project databases 2023` course at the University of Antwerp.

## Directory structure

```
|
|-- server (Python) - Core api package that handles recommendations and filtering.
|   |-- pyproject.toml - Pip package requirements and plugin configurations
|   |-- news_finder - Python flask source code
|   |-- test - Test files
|
|-- client (TypeScript) - Webpage built using ReactJS that interacts with the Python core.
|   |-- src - React source code
|
|-- db (SQL) - Database definition and migrations managed by Prisma.
|   |-- migrations - Set of migrations needed to construct the database
|   |-- schema.prisma - Database definition
|
|-- rss-scraper (Rust) - RSS scraping application that runs periodically
|   |-- src - Rust source code
|   |-- prisma-cli - Rust prisma client cli application
|
|-- similarity-checker (Python) - Article similarity checker that runs periodically
|   |-- similarity_checker - Python source code
|   |-- res - Text files with stop words for languages
|   |-- articles - Example articles used in development
|
|-- ...
```

## Quick start

### Using docker (production)

```bash
# start all containers
docker compose -f docker/docker-compose.yml up
# stop and remove all containers
docker compose -f docker/docker-compose.yml down
```

**Note**: when rebuilding first run `docker compose -f docker/docker-compose.yml build`.

**Note**: To access the front-end application go to route: `http://localhost:80`.
To access the back-end go to route: `http://localhost:80/api`

### Manual installation (development)

#### Server

##### 1. Install postgres

```bash
sudo apt install postgresql
```

##### 2. Create the database

First configure the database using the postgres user:

```bash
sudo su postgres
psql
```

Then create a role 'app' that will create the database and be used by the application:

```bash
CREATE ROLE ppdb_admin WITH LOGIN CREATEDB PASSWORD 'admin';
CREATE DATABASE ppdb OWNER ppdb_admin;
```

You need to 'trust' the role to be able to login.\
Add the following line to `/etc/postgresql/14/main/pg_hba.conf` (you need root access, version may vary). **It needs to be the first rule (above local all all peer).**

```
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# app
local   ppdb            ppdb_admin                              trust
```

Now you can restart postgres:

```bash
sudo systemctl restart postgresql
```

##### 3. Create virtual environment:

```bash
cd server
python -m venv venv
source venv/bin/activate
pip3 install .
```

**Note**: If installing for development use `pip3 install --editable .`

##### 4. Add tables to database:

```bash
prisma db push --schema ../db/schema.prisma
```

**(optional)** You can seed the database using:

```bash
python3 news_finder/seeding.py
```

#### Sidenote

When changing the database schema, always make sure to migrate before using `prisma db push`. The database will be cleared if this is done the other way around.

### Testing
The steps to setup the testing framework for the server are described [here](server/tests/README.md).

### Client

```bash
# pnpm
cd client
pnpm install
pnpm run start
```

```bash
# npm
cd client
npm install
npm run start
```

```bash
# yarn
cd client
yarn add
yarn start
```
