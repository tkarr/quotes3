CREATE TABLE items(
    item_no TEXT NOT NULL PRIMARY KEY,
    description TEXT,
    base_price DECIMAL DEFAULT 0,
    profit DECIMAL DEFAULT 10);

CREATE TABLE options(
    option_id SERIAL NOT NULL PRIMARY KEY,
    parent_id INT,
    description TEXT NOT NULL,
    uom TEXT, 
    stock_no TEXT);

CREATE TABLE enabled_options(
    id SERIAL NOT NULL PRIMARY KEY,
    item_no TEXT NOT NULL,
    option_id INT NOT NULL,
    sort_index INT DEFAULT 999);

CREATE TABLE reps(
    rep_no TEXT NOT NULL PRIMARY KEY,
    zip_codes TEXT[][2],
    discount DECIMAL);


