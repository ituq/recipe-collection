-- MySQL Schema for Recipe Database
-- Drop tables if they exist (in reverse order of creation to avoid foreign key constraints)
DROP TABLE IF EXISTS instructions;

DROP TABLE IF EXISTS ingredients;

DROP TABLE IF EXISTS recipes;

-- Main recipes table
CREATE TABLE recipes (
    id MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    image_url VARCHAR(500),
    rating DECIMAL(3, 2),
    rating_count MEDIUMINT UNSIGNED,
    preparation_time VARCHAR(100),
    original_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Ingredients table with foreign key relationship to recipes
CREATE TABLE ingredients (
    ingredient_number TINYINT UNSIGNED,
    recipe_id MEDIUMINT UNSIGNED,
    amount DECIMAL(8, 2),
    name VARCHAR(255) NOT NULL,
    PRIMARY KEY (recipe_id, ingredient_number),
    FOREIGN KEY (recipe_id) REFERENCES recipes (id) ON DELETE CASCADE
);

-- Instructions table with foreign key relationship to recipes
CREATE TABLE instructions (
    recipe_id MEDIUMINT UNSIGNED PRIMARY KEY,
    instructions TEXT NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes (id) ON DELETE CASCADE
) ENGINE = InnoDB ROW_FORMAT = COMPRESSED KEY_BLOCK_SIZE = 8;

-- 8KB compression blocks (can be 1, 2, 4, 8, or 16)
-- Create indexes for better performance
CREATE INDEX idx_recipe_title ON recipes (title);

CREATE INDEX idx_recipe_rating ON recipes (rating);

CREATE INDEX idx_recipe_rating_count ON recipes (rating_count);

CREATE INDEX idx_recipe_preparation_time ON recipes (preparation_time);

CREATE INDEX idx_ingredients_recipe ON ingredients (recipe_id);

CREATE INDEX idx_instructions_recipe ON instructions (recipe_id);
