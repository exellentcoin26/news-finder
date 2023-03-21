# Testing

The server uses pytest as it's testing framework. We will asume that you have completed the [manual installation](../../README.md#manual-installation) of the server. Follow these steps to set it up:

## 1. Create test database

First configure the database using the postgres user:

```bash
sudo su postgres
psql
```

Then create the test database:

```bash
CREATE DATABASE ppdb_test OWNER ppdb_admin;
```

You need to 'trust' the role to be able to login.\
Add the following line to `/etc/postgresql/14/main/pg_hba.conf` (you need root access, version may vary). **It needs to be the just below the line you put there during the installation.**

```
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# app
local   ppdb            ppdb_admin                              trust
local   ppdb_test       ppdb_admin                              trust
```

Now you can restart postgres:

```bash
sudo systemctl restart postgresql
```

## 2. Enter virtual evnironment

If you are not already in the virtual environment, enter it now.

```bash
cd server
source venv/bin/activate
```

## 3. Add tables to database

```bash
DATABASE_URL=postgres://ppdb_admin:admin@localhost:5432/ppdb_test
prisma db push --schema ../db/schema.prisma
```

## 4. Run pytest

```bash
pytest
```
