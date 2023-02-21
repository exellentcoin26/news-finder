# News finder

News aggregator application made for the `Project databases 2023` course at the University of Antwerp.

## Directory structure

```
|
|-- server (Python) - Core api package that handles recommendations and filtering.
|   |-- requirements.txt - Pip package requirements
|   |-- src - Python flask source code
|
|-- client (TypeScript) - Webpage built using ReactJS that interacts with the C++ core.
|   |-- src - React source code
|
|-- db (SQL) - Database definition and migrations managed by DbMate.
|   |-- schema.sql - Database sql definition
|   |-- migrations - Set of migrations needed to construct the database
|
|-- ...
```

## Quick start

### Server

```bash
cd server
pip3 install -r requirements
python3 main.py
```

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
