import mysql.connector
from mysql.connector import Error
from Recipe import Recipe, get_recipe_essen_trinken

def transfer_recipe_to_db(recipe: Recipe, host: str, database: str, user: str, password: str) -> bool:
    """
    Transfer a Recipe object to MySQL database
    Returns True if successful, False otherwise
    """
    try:
        # Connect to database
        connection = mysql.connector.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        cursor = connection.cursor()

        # Insert recipe
        recipe_query = """
            INSERT INTO recipes (title, image_url, rating, rating_count, preparation_time, original_url)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(recipe_query, (
            recipe.title,
            recipe.image_url,
            recipe.rating,
            recipe.rating_count,
            recipe.time,
            recipe.original_url
        ))
        recipe_id = cursor.lastrowid

        # Insert ingredients
        for i, (amount, ingredient_name) in enumerate(recipe.ingredients, 1):
            ingredient_query = """
                INSERT INTO ingredients (recipe_id, ingredient_number, amount, name)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(ingredient_query, (recipe_id, i, amount, ingredient_name))

        # Insert instructions
        instructions_text = "\n".join([f"{i+1}. {instruction}" for i, instruction in enumerate(recipe.instructions)])
        instruction_query = """
            INSERT INTO instructions (recipe_id, instructions)
            VALUES (%s, %s)
        """
        cursor.execute(instruction_query, (recipe_id, instructions_text))

        connection.commit()
        print(f"Successfully transferred recipe: {recipe.title}")
        return True

    except Error as e:
        print(f"Database error: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
