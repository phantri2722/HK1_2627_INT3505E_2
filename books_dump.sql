BEGIN TRANSACTION;
CREATE TABLE books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        price FLOAT NOT NULL);
INSERT INTO "books" VALUES(1,'API Design Pattern','Geewax',20.0);
INSERT INTO "books" VALUES(2,'Bup sen xanh','Son Tung',45.0);
INSERT INTO "books" VALUES(3,'Nuoc non van dam','Nguyen The Ky',75.0);
INSERT INTO "books" VALUES(4,'Clean Code','Robert Martin',10.0);
INSERT INTO "books" VALUES(5,'Clean Architecture','Robert Martin',15.0);
INSERT INTO "books" VALUES(6,'Fluent Python','Luciano Ramalho',17.0);
INSERT INTO "books" VALUES(7,'Effective Python','Bret Slatkin',25.0);
INSERT INTO "books" VALUES(8,'Python Crash Course','Eric Matthes',30.0);
INSERT INTO "books" VALUES(9,'Designing Data-Intensive Applications','Martin Kleppman',100.0);
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('books',9);
COMMIT;
