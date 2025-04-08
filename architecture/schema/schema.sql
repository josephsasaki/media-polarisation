DROP TABLE IF EXISTS topic;
DROP TABLE IF EXISTS article_topic;
DROP TABLE IF EXISTS article;
DROP TABLE IF EXISTS news_outlet;


CREATE TABLE topic (
    topic_id INT NOT NULL GENERATED ALWAYS AS IDENTITY,
    topic_name VARCHAR(20) NOT NULL,
    PRIMARY KEY (topic_id)
);

CREATE TABLE news_outlet (
    news_outlet_id INT NOT NULL GENERATED ALWAYS AS IDENTITY,
    news_outlet_name VARCHAR NOT NULL,
    PRIMARY KEY (news_outlet_id)
);


CREATE TABLE article (
    article_id BIGINT NOT NULL GENERATED ALWAYS AS IDENTITY,
    news_outlet_id INT NOT NULL,
    article_headline VARCHAR NOT NULL, 
    article_url VARCHAR(200) NOT NULL,
    article_published_date TIMESTAMP NOT NULL,
    article_subjectivity FLOAT NOT NULL,
    article_polarity FLOAT NOT NULL,
    PRIMARY KEY (article_id),
    FOREIGN KEY (news_outlet_id) REFERENCES  news_outlet(news_outlet_id)
);

CREATE TABLE article_topic (
    article_topic_id BIGINT NOT NULL GENERATED ALWAYS AS IDENTITY,
    article_id BIGINT NOT NULL,
    topic_id INT NOT NULL,
    article_topic_positive_sentiment FLOAT NOT NULL, 
    article_topic_negative_sentiment FLOAT NOT NULL,
    article_topic_neural_sentiment FLOAT NOT NULL,
    article_topic_compound_sentiment FLOAT NOT NULL,
    PRIMARY KEY (article_topic_id),
    FOREIGN KEY (article_id) REFERENCES article(article_id),
    FOREIGN KEY (topic_id) REFERENCES topic(topic_id)
);

-- Seeding the news_outlet table.

INSERT INTO news_outlet
(news_outlet_name)
VALUES
('The Guardian'),
('Daily Express');