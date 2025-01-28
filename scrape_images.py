import os
import time
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# outputs
output_folder = 'images'
os.makedirs(output_folder, exist_ok=True)

# Read the CSV file into a DataFrame
csv_file = 'extracted_links.csv'
df = pd.read_csv(csv_file)
print(f"Loaded CSV: {csv_file}")
print(df.head())

# Prepare to store the results
results = []

# Set up Selenium (uses Chrome WebDriver)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no browser UI)
chrome_driver_path = r'C:\Users\afu\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe'
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Loop through each URL in the 'url' column
for index, row in df.iterrows():
    url = row['url']
    

    # Step 1: Create the image page URL by appending /images to the original URL
    img_page_url = url+ '/images'
    print(img_page_url)
    
    driver.get(img_page_url)

    # Wait for content to load
    time.sleep(3)

    # Step 2: Get the page source and parse it
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    # Step 3: Find all divs with the class "usa-card"
    usa_cards = soup.find_all("div", class_="usa-card")
    found_non_copyrighted_image = False
    img_url = None

    for usa_card in usa_cards:
        # Check for the <p> with class "text-center" and find the <small> element
        text_center_p = usa_card.find("p", class_="text-center")
        if text_center_p:
            small_text = text_center_p.find("small")
            if small_text and small_text.text.strip().startswith("©"):
                print("Image is copyrighted, skipping...")
                continue  # Skip this image if it's copyrighted
        
        # If no copyright found, proceed to get the image URL and download
        img = usa_card.find("img")
        if img and img.get('src'):
            img_url = img.get('src')
            img_url = urljoin(img_page_url, img_url)  # Convert to absolute URL if needed
            found_non_copyrighted_image = True
            print(f"Found non-copyrighted image: {img_url}")
            break  # Exit the loop once we find a non-copyrighted image

    if found_non_copyrighted_image:
        # Download the image if a valid one was found
        try:
            img_response = requests.get(img_url)
            img_response.raise_for_status()  # Check if the request was successful

            # Save the image to the output folder
            image_name = os.path.basename(img_url)
            image_path = os.path.join(output_folder, image_name)

            with open(image_path, 'wb') as img_file:
                img_file.write(img_response.content)

            print(f"Image saved: {image_path}")
        except requests.RequestException as e:
            print(f"Error downloading image from {img_url}: {e}")
            img_url = None  # If there's an error, set the image URL as None
    else:
        print(f"No usable image found at {img_page_url}")
        img_url = None  # If no non-copyright image is found, set the image URL as None

    # Append the original URL and image URL to results
    results.append([url, img_url])

# Convert results into a DataFrame and save to a new CSV
results_df = pd.DataFrame(results, columns=['Original URL', 'Image URL'])
output_csv = 'updated_links.csv'
results_df.to_csv(output_csv, index=False)

print(f"Updated CSV saved as {output_csv}")

# Clean up and close the browser
driver.quit()