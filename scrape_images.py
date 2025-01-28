
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin


# outputs
output_folder = 'images'
os.makedirs(output_folder, exist_ok=True)

# Read the CSV file into a DataFrame
csv_file = 'extracted_links.csv' 
df = pd.read_csv(csv_file)
print(df.head())

# List to store image URLs
image_urls = []


# Set up Selenium (uses Chrome WebDriver)
chrome_options = Options()
chrome_options.add_argument("--headless")  
chrome_driver_path = (r'C:\Users\afu\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe')
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Prepare to store the results
results = []

# Loop
for index, row in df.iterrows():
    url = row['url'] 
    
    driver.get(url)

    # Wait for content to load (adjust time or use WebDriverWait for dynamic elements)
    time.sleep(2)

    # Get the fully loaded page source
    page_source = driver.page_source

    # Parse with BeautifulSoup
    soup = BeautifulSoup(page_source, "html.parser")

    # Example: Extracting data
    image = soup.find("img", class_="display-block")
    
    if image:
        # Get the image URL
        img_url = image.get('src')
        img_url = urljoin(url, img_url)  # Make sure the image URL is absolute
        
        # Get the image content
        try:
            img_response = requests.get(img_url)
            img_response.raise_for_status()
            
            # Extract the image name and save it
            image_name = os.path.basename(img_url)
            image_path = os.path.join(output_folder, image_name)
            
            with open(image_path, 'wb') as img_file:
                img_file.write(img_response.content)
            print(f"Image saved: {image_path}")
            image_urls.append(img_url)  # Append the image URL to the list
        except requests.RequestException as e:
            print(f"Error downloading image from {img_url}: {e}")
            image_urls.append(None)  # Append None if there's an error
    else:
        print(f"No image found at {url}")
        image_urls.append(None)  # Append None if no image is found

    # Append the original URL and image URL to results
    results.append([url, img_url])

    # Save the updated DataFrame to a new CSV file
    results_df = pd.DataFrame(results, columns=['Original URL', 'Image URL'])
    output_csv = 'updated_links.csv' 
    results_df.to_csv(output_csv, index=False)

    print(f"Updated CSV saved as {output_csv}")

    # Clean up and close the browser
    driver.quit()
    
    
    