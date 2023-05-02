# News Finder - Technical documentation

This document guides you through integrating this code base into your project
and how to expand it. It will not be a step-by-step, but rather an explanation
of our choices of technologies and what it means for you as the next developer.

## Integration

When we started developing the project, we immediately integrated tools to
streamline the development process. For example, tests are run automatically
with which the majority of the code base is tested. Another development goal
we had is that we should spend as little time as possible getting production
setup and running.

### Docker and docker compose

The best solution to this is to containerize all applications and use a
container management system to start and manage these containers. Suiting our
needs perfectly, we opted for docker compose. Every application that should be
run separately contains a Dockerfile script. This containerises and creates an
easy to use, configure, integrate and deploy image of the application.

### Configurability

The only settings we needed to configure in this project are the `DATABASE_URL`
and the `VITE_SERVER_URL`. Because security was not the biggest concern, we
opted to locate these in .env files. Any application that uses the database
needs one of these files. The latter is needed because the client needs to
comunicate with server.

### Database and ORM

The central part of the project is the database. Multiple applications need
access to it, which is done using the environment variables. However we would
also like this access to be type-safe, which is where prisma comes in. Prisma
allows us to define the entire database and its relation in a language
independent structure. This allows us to use multiple languages compared to
being restricted to a single ORM. Another feature we make handy use of is
database migrations. Included in the docker compose file is a dependency list
of containers, one of which assigned to migrating the database whenever
possible.

### How would you use it?

Because the entire project is structured into separately deployable services,
you can use it however and with whatever you like. The only steps needed are:

1. Checking out the project
2. Creating `.env` files with the `DATABASE_URL` environment set to any
postgres database you want to use. (other databases are possible, but require
some further configuration and are not tested with the current project.)
3. Add the `VITE_SERVER_URL` environment variable to the `client` directory.
(Using caddy this would be `/api`)
4. Build and start the docker containers

```shell
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml up
```

This results in all services being deployed, the client exposed on `0.0.0.0:80`
and the server exposed on `0.0.0.0:80/api`. All other services run on a
schedule. Which add entries to the database periodically.

## Expanding

Expanding the code base might be just as simple. Depending on how fluent you are
in the used technologiesl, it should be as straightforward as further working on
code you have written yourself. For an overview of these technologies you can
read the [project report](./docs/NewsFinder.pdf). Because the project is built
using small blocks that fit together and communicate over a network. It can be
extended with new functionalities either by creating new applications or
expanding the ones already present.

## Automatic deployment

Whenever someone pushes code to any of the branches, the code is checked out by
CircleCI and tested using type-checkers, compilers and test suites. However,
one additional step is done when pushing to the `main` branch. When all other
checks have finished and completed, the `deploy-to-gcp` job is started. One of
the requirements is that we use the
[google cloud platform](https://console.cloud.google.com) to host our project.
The single purpose of this job is to ssh into the virtual machine using a
service account we have setup on gcp and run the
[`deploy-docker-compose.sh`](./scripts/deploy-docker-compose.sh) script on the
server. When integrating automatic deployment into your own code base, you can
use the same script and the same steps as shown in the
[`.circleci/config.yml`](./.circleci/config.yml) file. The script can remain
the same, however some configuration might be needed to integrate with your
servers.

## Further reading

For more information you can read the [project report](./docs/NewsFinder.pdf)
and other README files present in the project.
