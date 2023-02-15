# News finder

News aggregator application made for the `Project databases 2023` course at the University of Antwerp.

## Directory structure

```
|
|-- server (C++) - Core api package that handles recommendations and filtering.
|   |-- src
|   |-- test
|
|-- client (TypeScript) - Webpage built using ReactJS that interacts with the C++ core.
|   |-- src - React source code
|
|-- ...
```

## Quick start

### Server

```bash
cd server
make run -j12
```

### Client

```bash
# pnpm
cd client
pnpm run start
```

```bash
# npm
cd client
npm run start
```

```bash
# yarn
cd client
yarn start
```
