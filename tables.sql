-- MySQL Schema for Recipe Database

-- Drop tables if they exist (in reverse order of creation to avoid foreign key constraints)
DROP TABLE IF EXISTS instructions;
DROP TABLE IF EXISTS ingredients;
DROP TABLE IF EXISTS recipes;

-- Main recipes table
CREATE TABLE recipes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    image_url VARCHAR(500),
    rating DECIMAL(3,2),
    rating_count INT,
    preparation_time VARCHAR(100),
    original_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Ingredients table with foreign key relationship to recipes
CREATE TABLE ingredients (
    ingredient_number TINYINT UNSIGNED UNIQUE NOT NULL ,
    recipe_id INT NOT NULL,
    amount INT,
    name VARCHAR(255) NOT NULL,
    PRIMARY KEY (recipe_id, ingredient_number)
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);

-- Instructions table with foreign key relationship to recipes
CREATE TABLE instructions (
    recipe_id INT NOT NULL PRIMARY KEY,
    instructions TEXT NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX idx_recipe_title ON recipes(title);
CREATE INDEX idx_recipe_rating ON recipes(rating);
CREATE INDEX idx_ingredients_recipe ON ingredients(recipe_id);
CREATE INDEX idx_instructions_recipe ON instructions(recipe_id);
