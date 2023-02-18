#include "crow.h"
#include "pqxx/pqxx"

#include <iostream>
#include <stdexcept>
#include <string_view>

int main() {
    try {
        // Connect to the database. Multiple connections can be created to the same database. Just some placeholder
        // values that should work when using the docker-compose file. See docker-compose for installation and running.
        pqxx::connection con("user = postgres password = password dbname = news-finder host = localhost port = 5432");

        // Create a transaction to start executing commands and queries. Only a single transaction can exist for a
        // single connection. When a transaction closes and commits, a new one can be created.
        pqxx::transaction t(con);

        // Execute create table command. Can only be run once (not used in practice). A database migration system will
        // be used to create sql tables.
        t.exec(R"(
            CREATE TABLE Uuser (
                id SERIAL PRIMARY KEY,
                name VARCHAR NOT NULL
            );
        )");

        // Insert placeholder data.
        t.exec(R"(INSERT INTO Uuser (name) values ('ayoub');)");
        t.exec(R"(INSERT INTO Uuser (name) values ('chloe');)");
        t.exec(R"(INSERT INTO Uuser (name) values ('david');)");
        t.exec(R"(INSERT INTO Uuser (name) values ('jonas');)");
        t.exec(R"(INSERT INTO Uuser (name) values ('laurens');)");

        // Query data from db.
        // Note: The `std::string_view` type reuses the original allocation of the string, but when the underlying
        // string is deleted, the buffer contents become undefined.
        for (auto [id, name] : t.query<unsigned long, std::string_view>(R"(SELECT * FROM Uuser;)")) {
            std::cout << "id: " << id << ", name: " << name << '\n';
        }

        // Commit the transaction. If not done, the transactio will be aborted and the db will be reverted.
        t.commit();
        std::cout << "committed work to database" << std::endl;

        con.close();

        // crow::SimpleApp app;
        // CROW_ROUTE(app, "/")([]() { return "Hello, world!"; });
        // app.port(18080).multithreaded().run();a

    } catch (const std::exception& e) {
        std::cout << e.what() << std::endl;

        // return non-zero exit code on error
        return 1;
    }

    return 0;
}
