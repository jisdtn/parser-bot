-- migrate:up
create table articles (
    id serial primary key,
    title varchar(400),
    link varchar(400),
    CONSTRAINT unique_link UNIQUE (link)
);


-- migrate:down
drop table if exists articles;