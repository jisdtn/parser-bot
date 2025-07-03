-- migrate:up
create table articles (
    id serial primary key,
    title varchar(200),
    link varchar(200),
    CONSTRAINT unique_link UNIQUE (link)
);


-- migrate:down
drop table if exists articles;