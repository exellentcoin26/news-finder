# Rss Scraper

Rss feed scraping and checking cli application written in rust.

## Usage

Running the rss-scraper requires an installation of `rust` and `cargo`.
Installation instructions can be found
[here](https://www.rust-lang.org/tools/install "rust installation")
(https://www.rust-lang.org/tools/install).

The project is tested on linux with `rustc` version `>=1.68.0`.

### Setup

The first step in building the project is generating prisma database
definitions. To do this, you will need to install the `prisma` cli from either
`pip` or `npm`. The builtin prisma cli does not allow the `--generator` flag
which is needed for this project. Installation of which will not be documented.

In all further commands we will assume that your current working directory is
the `rss-scraper` directory.

To generate the prisma definitions run the following command.

```shell
prisma generate --schema ../db/schema.prisma --generator rss-scraper
```

~~Note: This might take quite some time depending on your hardware.~~

### Running the scraper

The application is divided into two parts, with the first part being the actual
rss scraper. To run the scraper either build the application first and then run
as a regular binary or run it using the `cargo` command provided by the `rust`
build system (the latter will be used in this explanation). Every command
provided can also be run with the `--release` flag for better runtime
performance.

```shell
cargo run -- run --help
```

This will print a help message about provided commands. Commands can be
specified to the `rss-scraper` cli by prefixing with `--` as shown here.
Anything before the prefix is supplied to the `cargo` binary. Anything after is
supplied to the `rss-scraper` cli.

```shell
cargo run -- run --once
```

For further documentation refer to the cli help pages.

### Checking input files

The second part of the application allows verifying the validity of RSS feeds
against the rss-scraper.

The input file is expected to be RSS feed links separated by newlines.

Help pages about this part of the project can be found using the following
command.

```shell
cargo run -- check --help
```

For further documentation refer to the cli help pages.

## Provided files

The [`rss-feeds.txt`](./rss-feeds.txt) file is a list of rss feeds already
checked by us.
