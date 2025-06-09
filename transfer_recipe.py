import pymysql
from pymysql import Error
from Recipe import Recipe, get_recipe_essen_trinken
import os
import time

password = open('password.txt', 'r').read().strip()

def transfer_recipe_to_db(recipe: Recipe) -> bool:
    """
    Transfer a Recipe object to MySQL database
    Returns True if successful, False otherwise
    """
    connection = None
    cursor = None
    try:
        # Connect to database
        connection = pymysql.connect(
            host="mysql1.ethz.ch",
            user="vifranz",
            password=password,
            database="vifranz",
            charset="utf8"
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
        if cursor:
            cursor.close()
        if connection and connection.open:
            connection.close()

def read_recipe_urls(filename: str) -> list[str]:
    """
    Read recipe URLs from a text file
    Returns a list of URLs, skipping empty lines and comments
    """
    urls = []
    if not os.path.exists(filename):
        print(f"Error: {filename} not found")
        return urls

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                # Skip empty lines and comments (lines starting with #)
                if line and not line.startswith('#'):
                    if line.startswith('https://www.essen-und-trinken.de/'):
                        urls.append(line)
                    else:
                        print(f"Warning: Skipping invalid URL on line {line_num}: {line}")
    except Exception as e:
        print(f"Error reading {filename}: {e}")

    return urls

def process_all_recipes(url_file: str = 'recipe_urls.txt', delay: float = 1.0) -> dict:
    """
    Process all recipes from the URL file and transfer them to database

    Args:
        url_file: Path to file containing recipe URLs
        delay: Delay in seconds between requests (to be respectful to the server)

    Returns:
        Dictionary with processing results
    """
    urls = read_recipe_urls(url_file)

    if not urls:
        print("No valid URLs found to process")
        return {'successful': 0, 'failed': 0, 'skipped': 0, 'details': []}

    print(f"Found {len(urls)} URLs to process")

    results = {
        'successful': 0,
        'failed': 0,
        'skipped': 0,
        'details': []
    }

    for i, url in enumerate(urls, 1):
        print(f"\n--- Processing recipe {i}/{len(urls)} ---")
        print(f"URL: {url}")

        try:
            # Fetch recipe from website
            print("Fetching recipe...")
            recipe = get_recipe_essen_trinken(url)
            print(f"Retrieved: {recipe.title}")

            # Transfer to database
            print("Transferring to database...")
            success = transfer_recipe_to_db(recipe)

            if success:
                results['successful'] += 1
                results['details'].append(f"✅ {recipe.title}")
                print(f"✅ Successfully processed: {recipe.title}")
            else:
                results['failed'] += 1
                results['details'].append(f"❌ Database error: {recipe.title}")
                print(f"❌ Failed to transfer: {recipe.title}")

        except Exception as e:
            results['failed'] += 1
            error_msg = f"❌ Error processing {url}: {str(e)}"
            results['details'].append(error_msg)
            print(error_msg)

        # Add delay between requests to be respectful to the server
        if i < len(urls):  # Don't delay after the last request
            print(f"Waiting {delay} seconds before next request...")
            time.sleep(delay)

    return results

def main():
    """Main function to run the recipe processing"""
    print("Recipe Transfer Tool")
    print("=" * 50)

    # Process all recipes from recipe_urls.txt
    results = process_all_recipes()

    # Print summary
    print("\n" + "=" * 50)
    print("PROCESSING SUMMARY")
    print("=" * 50)
    print(f"Total URLs processed: {results['successful'] + results['failed']}")
    print(f"Successfully transferred: {results['successful']}")
    print(f"Failed transfers: {results['failed']}")

    if results['details']:
        print("\nDetailed Results:")
        for detail in results['details']:
            print(detail)

if __name__ == "__main__":
    main()
