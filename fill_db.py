#fill database with data from urls in in urls.txt
password = open('password.txt', 'r').read().strip()
from string import printable
import mysql.connector
urls = open('urls.txt', 'r')
from Recipe import Recipe, get_recipe_essen_trinken

for url in urls:
    recipe = get_recipe_essen_trinken(url)

    connection = mysql.connector.connect(
        host="mysql1.ethz.ch",
            user="vifranz",
            password=password,
            database="vifranz",
            charset="utf8",
            ssl_disabled=True
    )

    cursor = connection.cursor()
    cursor.execute("INSERT INTO recipes (name, ingredients, instructions) VALUES (%s, %s, %s)", (recipe.name, recipe.ingredients, recipe.instructions))
    cursor.close()
    connection.close()
