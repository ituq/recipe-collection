#!/bin/bash

# Script to harvest recipe URLs from essen-und-trinken.de monthly archives
# Uses predictable URL format: ?month=M&year=YYYY
# Archive goes back to 01.2007

BASE_URL="https://www.essen-und-trinken.de"
ARCHIVE_BASE="$BASE_URL/rezepte/archiv/"
OUTPUT_FILE="recipe_urls.txt"
TEMP_DIR=$(mktemp -d)

echo "Harvesting recipe URLs from monthly archives (2007-2025)..."
echo "========================================================"

# Function to extract recipe URLs from a single archive page
extract_recipes_from_page() {
    local page_url="$1"
    local temp_file="$2"
    
    curl -s -L \
         -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
         "$page_url" > "$temp_file"
    
    if [ ! -s "$temp_file" ]; then
        return
    fi
    
    # Extract recipe URLs (not archive URLs)
    grep -oE 'href="[^"]*"' "$temp_file" | \
    sed 's/href="//g' | \
    sed 's/"$//g' | \
    grep '/rezepte/' | \
    grep -v '/archiv/' | \
    grep -v '^#' | \
    while IFS= read -r url; do
        if [[ $url == http* ]]; then
            echo "$url"
        elif [[ $url == /* ]]; then
            echo "$BASE_URL$url"
        else
            echo "$BASE_URL/rezepte/$url"
        fi
    done
}

# Get current year and month
CURRENT_YEAR=$(date +%Y)
CURRENT_MONTH=$(date +%m)

# Initialize output file
> "$OUTPUT_FILE"
ALL_RECIPES="$TEMP_DIR/all_recipes.txt"
> "$ALL_RECIPES"

echo "Writing URLs live to: $OUTPUT_FILE"

total_archives=0
processed=0

# Calculate total number of archives for progress
for year in $(seq 2007 $CURRENT_YEAR); do
    if [ $year -eq $CURRENT_YEAR ]; then
        # For current year, include all months up to current month
        total_archives=$((total_archives + CURRENT_MONTH))
    else
        total_archives=$((total_archives + 12))
    fi
done

echo "Processing $total_archives monthly archives..."
echo ""

# Loop through years and months
for year in $(seq 2007 $CURRENT_YEAR); do
    if [ $year -eq $CURRENT_YEAR ]; then
        # For current year, go up to current month (both formats work)
        max_month=$CURRENT_MONTH
    else
        max_month=12
    fi
    
    for month in $(seq 1 $max_month); do
        processed=$((processed + 1))
        
        # Construct URL
        archive_url="${ARCHIVE_BASE}?month=${month}&year=${year}"
        
        # Progress indicator
        printf "[\033[32m%3d/%d\033[0m] %02d.%04d: " $processed $total_archives $month $year
        
        # Extract recipes from this month
        temp_page="$TEMP_DIR/page_${year}_${month}.html"
        recipes_before=$(wc -l < "$ALL_RECIPES")
        
        extract_recipes_from_page "$archive_url" "$temp_page" | tee -a "$ALL_RECIPES" >> "$OUTPUT_FILE"
        
        recipes_after=$(wc -l < "$ALL_RECIPES")
        new_recipes=$((recipes_after - recipes_before))
        
        if [ $new_recipes -gt 0 ]; then
            printf "\033[32m+%d recipes\033[0m\n" $new_recipes
        else
            printf "\033[90mno recipes\033[0m\n"
        fi
        
        # Small delay to be respectful to the server
        sleep 0.3
    done
done

echo ""
echo "Processing results..."

# Remove duplicates and sort (final cleanup)
sort "$OUTPUT_FILE" | uniq | grep -v '^$' > "$TEMP_DIR/final_urls.txt"
mv "$TEMP_DIR/final_urls.txt" "$OUTPUT_FILE"

# Clean up temporary files
rm -rf "$TEMP_DIR"

# Display results
URL_COUNT=$(wc -l < "$OUTPUT_FILE")
echo ""
echo "==========================================="
echo "Total unique recipe URLs found: $URL_COUNT"
echo "URLs saved to: $OUTPUT_FILE"
echo "Archive period: 01.2007 - $(printf "%02d.%04d" $CURRENT_MONTH $CURRENT_YEAR)"

if [ "$URL_COUNT" -gt 0 ]; then
    echo ""
    echo "Sample URLs (first 10):"
    echo "----------------------"
    head -10 "$OUTPUT_FILE" | nl
    
    if [ "$URL_COUNT" -gt 10 ]; then
        echo "... and $((URL_COUNT - 10)) more URLs"
    fi
else
    echo "Warning: No URLs found. The page structure might have changed."
fi

echo ""
echo "Script completed!"