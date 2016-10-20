create table raw_news (
    id                 serial primary key,
    content_of_news    text,
    publish_date       timestamp,
    source_url         text,
    article_url        text
);

create table geo_news (
    id               serial primary key,
    raw_news_id        int references raw_news (id),
    coord              point
);

create table news (
    id                 serial primary key,
    geo_news_id        int references geo_news (id),
    category           int
);
