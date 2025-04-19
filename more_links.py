import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from difflib import SequenceMatcher

# Set up Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def generate_symbol(genus, species, suffix=''):
    genus_part = genus[:2].lower()
    species_words = species.split()
    species_part = species_words[0][:2].lower() if species_words else ''
    return genus_part + species_part + suffix

def check_usda_page(symbol, genus, species):
    # url = f"https://plants.usda.gov/plant-profile/{symbol}"
    url = 'https://plants.usda.gov/plant-profile/VIRO2'
    driver.get(url)
    time.sleep(2)

    try:
        header = driver.find_element("css selector", "h1 span").text.strip()
        target = f"{genus} {species}".strip()

        if all(token.lower() in header.lower() for token in target.split()):
            return url
        elif similar(header, target) > 0.85:
            return url
    except Exception:
        pass
    return None

# Load input JSON
with open("species_taxon_link.json", "r") as f:
    species_data = json.load(f)

unmatched = []
for item in species_data:
    if item["externallink"]:
        continue  # Skip if already filled

    genus = item.get("name_genus", "")
    species = item.get("name_species", "")
    found = False

    for suffix in ['', '2', '3', '4']:
        symbol = generate_symbol(genus, species, suffix)
        url = check_usda_page(symbol, genus, species)
        if url:
            item["externallink"] = url
            found = True
            break

    if not found:
        unmatched.append(item)

# Write updated JSON
with open("output_species_with_links.json", "w") as f:
    json.dump(species_data, f, indent=4)

# Write unmatched to a separate file
with open("unmatched_species.json", "w") as f:
    json.dump(unmatched, f, indent=4)

print(f"Completed. {len(species_data) - len(unmatched)} matched, {len(unmatched)} unmatched.")
