#!/usr/bin/env python3
"""
Simple script to run the recipe harvesting process
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from harvesting import get_recipe_urls_from_archive, harvest_all_recipes, save_urls_to_file, save_recipes_to_file
    from Recipe import get_recipe_essen_trinken
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure Recipe.py and harvesting.py are in the same directory")
    sys.exit(1)

def main():
    print("Essen & Trinken Recipe Harvester")
    print("=" * 40)
    print()
    
    while True:
        print("What would you like to do?")
        print("1. Get all recipe URLs only")
        print("2. Test with 5 recipes")
        print("3. Harvest 50 recipes")
        print("4. Harvest ALL recipes (this will take a long time!)")
        print("5. Exit")
        print()
        
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            print("\nGetting all recipe URLs...")
            try:
                urls = get_recipe_urls_from_archive()
                if urls:
                    filename = f"recipe_urls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    save_urls_to_file(urls, filename)
                    print(f"Success! Found {len(urls)} recipe URLs")
                    print(f"Saved to: {filename}")
                else:
                    print("No URLs found!")
            except Exception as e:
                print(f"Error: {e}")
        
        elif choice == "2":
            print("\nTesting with 5 recipes...")
            try:
                recipes = harvest_all_recipes(max_recipes=5)
                if recipes:
                    filename = f"test_recipes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    save_recipes_to_file(recipes, filename)
                    print(f"Success! Processed {len(recipes)} recipes")
                    print(f"Saved to: {filename}")
                else:
                    print("No recipes processed!")
            except Exception as e:
                print(f"Error: {e}")
        
        elif choice == "3":
            print("\nHarvesting 50 recipes...")
            try:
                recipes = harvest_all_recipes(max_recipes=50)
                if recipes:
                    filename = f"recipes_50_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    save_recipes_to_file(recipes, filename)
                    print(f"Success! Processed {len(recipes)} recipes")
                    print(f"Saved to: {filename}")
                else:
                    print("No recipes processed!")
            except Exception as e:
                print(f"Error: {e}")
        
        elif choice == "4":
            print("\nWARNING: This will harvest ALL recipes and may take several hours!")
            confirm = input("Are you sure? (yes/no): ").strip().lower()
            if confirm == "yes":
                print("\nHarvesting ALL recipes...")
                try:
                    recipes = harvest_all_recipes()
                    if recipes:
                        filename = f"all_recipes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                        save_recipes_to_file(recipes, filename)
                        print(f"Success! Processed {len(recipes)} recipes")
                        print(f"Saved to: {filename}")
                    else:
                        print("No recipes processed!")
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print("Cancelled.")
        
        elif choice == "5":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter 1-5.")
        
        print("\n" + "-" * 40 + "\n")

if __name__ == "__main__":
    main()