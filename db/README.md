# Database design and workflow

The database is fully managed using the [dbmate](https://github.com/amacneil/dbmate)
executable. You can create migrations and upload them to the database using the
commands `new <migration_name>` and `up`.

The [`schema.sql`] file is fully generated and maintained by dbmate and should
not be edited. It serves as a reference to the structure of the database.
