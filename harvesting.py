import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin
import re
from Recipe import get_recipe_essen_trinken

def get_recipe_urls_from_archive(archive_url="https://www.essen-und-trinken.de/rezepte/archiv/", page_limit=None):
    """
    Extract all recipe URLs from the Essen und Trinken recipe archive
    
    Args:
        archive_url: URL of the recipe archive
        page_limit: Maximum number of archive pages to process (None = all pages)
        
    Returns:
        List of recipe URLs
    """
    all_recipe_urls = set()
    current_page = 1
    base_url = "https://www.essen-und-trinken.de"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }
    
    while True:
        # Construct URL for current page
        if current_page == 1:
            url = archive_url
        else:
            url = f"{archive_url}?page={current_page}"
            
        print(f"Fetching page {current_page}: {url}")
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching page {current_page}: {e}")
            break
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all recipe links on this page
        recipe_links = []
        
        # Look for links in the recipe sections
        # Recipe links usually have patterns like /rezepte/recipe-name-rezept-12345.html
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href')
            if href and '/rezepte/' in href and '-rezept-' in href:
                # Convert relative URLs to absolute URLs
                if href.startswith('/'):
                    full_url = base_url + href
                else:
                    full_url = href
                    
                # Validate that it's a proper recipe URL
                if full_url.startswith('https://www.essen-und-trinken.de/rezepte/') and full_url.endswith('.html'):
                    recipe_links.append(full_url)
        
        # Remove duplicates from this page
        page_recipes = list(set(recipe_links))
        print(f"Found {len(page_recipes)} recipe URLs on page {current_page}")
        
        # If no recipes found on this page, we've reached the end
        if not page_recipes:
            print("No more recipes found. Stopping.")
            break
            
        # Add to our collection
        all_recipe_urls.update(page_recipes)
        
        # Check if we should continue to next page
        if page_limit and current_page >= page_limit:
            print(f"Reached page limit of {page_limit}")
            break
            
        # Look for next page link or pagination indicators
        next_page_found = False
        pagination_links = soup.find_all('a', href=True)
        for link in pagination_links:
            if 'page=' in link.get('href', '') or 'weiter' in link.text.lower() or 'next' in link.text.lower():
                next_page_found = True
                break
                
        # Also check if there are more articles by looking at the content
        # If we don't find pagination but still found recipes, try next page anyway
        if not next_page_found and len(page_recipes) < 10:  # Assume pages should have more recipes
            print("No clear pagination found and few recipes on page. Stopping.")
            break
            
        current_page += 1
        
        # Be respectful to the server
        time.sleep(1)
        
        # Safety check - don't go beyond reasonable number of pages
        if current_page > 100:
            print("Reached maximum page limit (100). Stopping.")
            break
    
    return list(all_recipe_urls)

def save_urls_to_file(urls, filename="recipe_urls.json"):
    """Save URLs to a JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(urls, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(urls)} URLs to {filename}")

def load_urls_from_file(filename="recipe_urls.json"):
    """Load URLs from a JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File {filename} not found")
        return []

def harvest_all_recipes(max_recipes=None, save_progress=True):
    """
    Harvest all recipes from the archive
    
    Args:
        max_recipes: Maximum number of recipes to process (None = all)
        save_progress: Whether to save progress periodically
        
    Returns:
        List of Recipe objects
    """
    print("Step 1: Getting all recipe URLs...")
    urls = get_recipe_urls_from_archive()
    
    if not urls:
        print("No URLs found!")
        return []
        
    print(f"Found {len(urls)} recipe URLs")
    
    # Save URLs for future use
    save_urls_to_file(urls)
    
    # Limit if specified
    if max_recipes:
        urls = urls[:max_recipes]
        print(f"Limited to first {len(urls)} recipes")
    
    print("Step 2: Extracting recipe details...")
    recipes = []
    failed_urls = []
    
    for i, url in enumerate(urls, 1):
        print(f"Processing recipe {i}/{len(urls)}: {url}")
        
        try:
            recipe = get_recipe_essen_trinken(url)
            recipes.append(recipe)
            
            # Save progress every 10 recipes
            if save_progress and i % 10 == 0:
                save_recipes_to_file(recipes, f"recipes_progress_{i}.json")
                
        except Exception as e:
            print(f"Failed to process {url}: {e}")
            failed_urls.append(url)
            
        # Be respectful to the server
        time.sleep(0.5)
    
    print(f"\nCompleted! Successfully processed {len(recipes)} recipes")
    if failed_urls:
        print(f"Failed to process {len(failed_urls)} URLs")
        save_urls_to_file(failed_urls, "failed_urls.json")
    
    return recipes

def save_recipes_to_file(recipes, filename="all_recipes.json"):
    """Save recipes to a JSON file"""
    recipes_data = []
    for recipe in recipes:
        recipe_dict = {
            'title': recipe.title,
            'ingredients': recipe.ingredients,
            'instructions': recipe.instructions,
            'image_url': recipe.image_url,
            'rating': recipe.rating,
            'rating_count': recipe.rating_count,
            'time': recipe.time
        }
        recipes_data.append(recipe_dict)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(recipes_data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(recipes)} recipes to {filename}")

def main():
    """Main function to run the harvesting process"""
    print("Recipe Harvester for Essen und Trinken")
    print("=====================================")
    
    # Option 1: Just get URLs
    print("\nOption 1: Get all recipe URLs only")
    urls = get_recipe_urls_from_archive()
    save_urls_to_file(urls)
    
    # Option 2: Get a few complete recipes as test
    print(f"\nOption 2: Process first 5 recipes as test")
    test_recipes = harvest_all_recipes(max_recipes=5)
    if test_recipes:
        save_recipes_to_file(test_recipes, "test_recipes.json")
    
    print("\nDone! Check the generated JSON files:")
    print("- recipe_urls.json: All recipe URLs")
    print("- test_recipes.json: First 5 complete recipes")
    print("\nTo process all recipes, call harvest_all_recipes() without max_recipes parameter")

if __name__ == "__main__":
    main()