select * from books;

SELECT
    tc.table_schema, 
    tc.constraint_name, 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_schema AS foreign_table_schema,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
      AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
      AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'PRIMARY KEY';

ALTER TABLE books
ADD PRIMARY KEY (isbn);

alter table books
ALTER COLUMN year set data TYPE varchar;

create table usuarios (
    id serial primary key,
    username text,
    pass text
) 

create table reseñas(
    id serial primary KEY,
    id_book varchar,
    id_usuario integer, 
    comentarios text,
    puntaje integer,
    FOREIGN KEY (id_book) REFERENCES books(isbn),
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
)