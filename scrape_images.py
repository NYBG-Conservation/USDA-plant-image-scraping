import os
import time
import requests
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# outputs
output_folder = 'images_2'
os.makedirs(output_folder, exist_ok=True)

results = []
# Read the CSV file into a DataFrame
csv_file = 'extracted_links_2.csv'
df = pd.read_csv(csv_file)
print(f"Loaded CSV: {csv_file}")
print(df.head())

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = Options()
chrome_options.add_argument("--headless")  # if you're running headless

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Loop through each URL in the 'url' column
for index, row in df.iterrows():
    url = row['externallink']
    img_page_url = url + '/images'
    print(img_page_url)
    
    driver.get(img_page_url)
    time.sleep(3)

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    usa_cards = soup.find_all("div", class_="usa-card")

    found_image = False
    img_url = None
    attribution = None

    for usa_card in usa_cards:
        text_center_p = usa_card.find("p", class_="text-center")
        is_copyrighted = False
        if text_center_p:
            small_text = text_center_p.find("small")
            if small_text:
                attribution = small_text.text.strip()
                if attribution.startswith("©"):
                    print("Image is copyrighted, skipping...")
                    continue  # Skip this image
        else:
            attribution = None  # Clear in case we found something before

        img = usa_card.find("img")
        if img and img.get('src'):
            img_url = urljoin(img_page_url, img.get('src'))
            print(f"✅ Found image: {img_url}")
            found_image = True
            break  # Exit after first valid image

    if found_image:
        try:
            img_response = requests.get(img_url)
            img_response.raise_for_status()

            image_name = os.path.basename(img_url)
            image_path = os.path.join(output_folder, image_name)

            with open(image_path, 'wb') as img_file:
                img_file.write(img_response.content)

            print(f"💾 Image saved: {image_path}")
        except requests.RequestException as e:
            print(f"❌ Error downloading image from {img_url}: {e}")
            img_url = None
    else:
        print(f"⚠️ No usable image found at {img_page_url}")
        img_url = None
        attribution = None

    # Save results (including attribution)
    results.append([url, img_url, attribution])

# Save to CSV
results_df = pd.DataFrame(results, columns=['Original URL', 'Image URL', 'Attribution'])
output_csv = 'updated_links_2.csv'
results_df.to_csv(output_csv, index=False)

print(f"✅ Updated CSV saved as {output_csv}")
driver.quit()
