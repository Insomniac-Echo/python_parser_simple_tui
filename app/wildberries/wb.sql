-- Table: trands
CREATE TABLE trands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_src INT UNIQUE NOT NULL, -- Unique identifier for the product
    rating FLOAT,
    reviewRating FLOAT,
    feedbacks INT,
    basic_price INT,
    product_price INT,
    total_price INT,
    count_sales INT,
    on_stock INT,
    date_of TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: trands_info
CREATE TABLE trands_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_trands INT NOT NULL, -- Foreign key to trands.id_src
    name VARCHAR(500),
    brand VARCHAR(500),
    sale VARCHAR(5),
    cashback VARCHAR(5),
    link TEXT,
    img_link TEXT,
    FOREIGN KEY (id_trands) REFERENCES trands(id_src) ON DELETE CASCADE
);

-- Table: category_trands
CREATE TABLE category_trands (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_trands INT NOT NULL, -- Foreign key to trands.id_src
    category_ru VARCHAR(500),
    category_eng VARCHAR(500),
    category_id INT,
    parent_id INT,
    FOREIGN KEY (id_trands) REFERENCES trands(id_src) ON DELETE CASCADE
);

-- Table: products
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_src INT UNIQUE NOT NULL, -- Unique identifier for the product
    name VARCHAR(500),
    cashback FLOAT,
    sale INT,
    brand VARCHAR(500),
    rating INT,
    supplier VARCHAR(500),
    supplierRating FLOAT,
    feedbacks INT,
    reviewRating FLOAT,
    promoTextCard TEXT,
    basic_price INT,
    product_price INT,
    total_price INT,
    logistics_price INT,
    return_price INT,
    link TEXT,
    img_link TEXT,
    description TEXT,
    category_ru VARCHAR(500),
    category_eng VARCHAR(500),
    category_id INT,
    parent_id INT
);

-- Indexes for performance
CREATE INDEX idx_trands_id_src ON trands(id_src);
CREATE INDEX idx_trands_info_id_trands ON trands_info(id_trands);
CREATE INDEX idx_category_trands_id_trands ON category_trands(id_trands);
CREATE INDEX idx_products_id_src ON products(id_src);