import requests
from bs4 import BeautifulSoup, Tag

class Recipe:
    def __init__(self, title: str, ingredients: list[tuple[float, str]], instructions: list[str], image_url: str, rating: float, rating_count: int, time: str, original_url: str):
        self.title = title
        self.ingredients = ingredients
        self.instructions = instructions
        self.image_url = image_url
        self.rating = rating
        self.rating_count = rating_count
        self.time = time
        self.original_url = original_url

    def __str__(self):
        image_info = f"\nImage: {self.image_url}" if self.image_url else ""
        rating_info = f"\nRating: {self.rating}/5" if self.rating else ""
        if self.rating_count:
            rating_info += f" ({self.rating_count} reviews)"
        time_info = f"\nTime: {self.time}" if self.time else ""

        # Format ingredients with one per line
        ingredients_formatted = "\n".join([f"- {amount} {ingredient}" for amount, ingredient in self.ingredients])

        # Format instructions with numbered steps
        instructions_formatted = "\n".join([f"{i+1}. {instruction}" for i, instruction in enumerate(self.instructions)])

        return f"{self.title}{image_info}{rating_info}{time_info}\n\nINGREDIENTS:\n{ingredients_formatted}\n\nINSTRUCTIONS:\n{instructions_formatted}"

def get_recipe_essen_trinken(url: str) -> Recipe:
    """
    Scrape recipe information from essen-und-trinken.de

    Args:
        url: The URL of the recipe page

    Returns:
        Recipe object with title, ingredients, instructions, and image URL

    The function extracts:
    - Title from the recipe headline
    - Ingredients with amounts and units
    - Instructions as a list of steps
    - Main recipe image URL (highest resolution available)
    - Rating (out of 5) and rating count
    - Recipe preparation time
    """
    if not url.startswith("https://www.essen-und-trinken.de/rezepte"):
        raise ValueError("Invalid URL")

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "no-cache",
        "dnt": "1",
        "pragma": "no-cache",
        "priority": "u=0, i",
        "sec-ch-ua": "\"Chromium\";v=\"137\", \"Not/A)Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    # Parse image URL
    image_url = None
    recipe_image_div = soup.find('div', class_='recipe-meta__image')
    if recipe_image_div:
        img_tag = recipe_image_div.find('img', class_='image')
        if img_tag:
            # First try to get the highest resolution image from srcset
            if img_tag.get('srcset'):
                srcset = img_tag.get('srcset')
                # Parse srcset format "url1 width1w, url2 width2w, ..."
                sources = [src.strip().split(' ') for src in srcset.split(',')]
                # Find the highest resolution image (with largest width)
                highest_res = None
                highest_width = 0
                for source in sources:
                    if len(source) >= 2 and source[1].endswith('w'):
                        try:
                            width = int(source[1].rstrip('w'))
                            if width > highest_width:
                                highest_width = width
                                highest_res = source[0]
                        except ValueError:
                            continue

                if highest_res:
                    image_url = highest_res

            # Fallback to src if no srcset or parsing failed
            if not image_url:
                image_url = img_tag.get('src')

    # Parse title
    title_div = soup.find('span', class_='title__headline u-typo u-typo--article-title')
    title = title_div.text.strip() if title_div is not None else "Recipe Title"

    # Parse ingredients
    ingredients = []
    ingredient_section = soup.find('section', class_='recipe-ingredients')

    if ingredient_section and isinstance(ingredient_section, Tag):
        # Process ingredient amounts
        amount_elements = ingredient_section.select('x-beautify-number.recipe-ingredients__amount')
        label_elements = ingredient_section.select('p.recipe-ingredients__label')

        for i in range(len(amount_elements)):
            if i < len(label_elements):
                amount_el = amount_elements[i]
                label_el = label_elements[i]

                # Extract amount
                try:
                    amount_str = amount_el.get('value', '')
                    if amount_str and amount_str.strip():
                        amount = float(amount_str.replace(',', '.'))
                    else:
                        amount = 0.0
                except (ValueError, TypeError):
                    amount = 0.0

                # Extract unit and ingredient name
                unit = ""
                unit_singular_el = label_el.select_one('span.recipe-ingredients__unit-singular')
                unit_plural_el = label_el.select_one('span.recipe-ingredients__unit-plural')

                if unit_singular_el and isinstance(unit_singular_el, Tag) and unit_singular_el.text.strip():
                    unit = unit_singular_el.text.strip()
                elif unit_plural_el and isinstance(unit_plural_el, Tag) and unit_plural_el.text.strip():
                    unit = unit_plural_el.text.strip()

                # Extract ingredient name
                ingredient_name = ""
                ingredient_span = label_el.select_one('span[data-label=""]')
                if ingredient_span and isinstance(ingredient_span, Tag):
                    ingredient_name = ingredient_span.text.strip()

                # Create final ingredient string
                full_ingredient = f"{unit} {ingredient_name}".strip() if unit else ingredient_name
                ingredients.append((amount, full_ingredient))

    # Parse instructions
    instructions = []
    instructions_section = soup.find('div', class_='group--preparation-steps')

    if instructions_section and isinstance(instructions_section, Tag):
        instruction_items = instructions_section.select('li.group__text-element')
        for item in instruction_items:
            text_element = item.select_one('div.text-element')
            if text_element and isinstance(text_element, Tag):
                instruction_text = text_element.text.strip()
                if instruction_text:
                    instructions.append(instruction_text)

    # Parse rating
    rating = None
    rating_count = None
    rating_div = soup.find('div', class_='recipe-rating')
    if rating_div:
        # Find the x-rating element with the value attribute
        rating_element = rating_div.find('x-rating')
        if rating_element and rating_element.has_attr('value'):
            try:
                rating = float(rating_element['value'])
            except (ValueError, TypeError):
                pass

        # Extract the rating count from the span with class recipe-rating__count
        count_span = rating_div.select_one('span.recipe-rating__count')
        if count_span:
            count_text = count_span.text.strip()
            # Extract number from format like "(77)"
            if count_text and count_text.startswith('(') and count_text.endswith(')'):
                try:
                    rating_count = int(count_text[1:-1])
                except (ValueError, TypeError):
                    pass

    # Parse recipe time
    time = None
    time_div = soup.find('div', class_='recipe-meta__item recipe-meta__item--cook-time')
    if time_div:
        time_span = time_div.select_one('span.u-typo.u-typo--recipe-info-text')
        if time_span:
            time = time_span.text.strip()
    return Recipe(title, ingredients, instructions, image_url, rating, rating_count, time,url)

url="https://www.essen-und-trinken.de/rezepte/85396-rzpt-fenchel-garnelen-pfanne#disqus_embed"

print(get_recipe_essen_trinken(url))
