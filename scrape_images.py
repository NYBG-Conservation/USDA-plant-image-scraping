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

# List to store image URLs
image_urls = []

# Loop
for index, row in df.iterrows():
    url = row['url'] 
    
    # Request
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check 
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        image_urls.append(None)  # Append None if there's an error
        continue
    
    print(response.text)
    
    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the image with the class
    image_tag = soup.find('img', class_='display-block')
    
    
    
    if image_tag:
        # Get the image URL
        img_url = image_tag.get('src')
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

# Add the new 'image_url' column to the DataFrame
df['image_url'] = image_urls

# Save the updated DataFrame to a new CSV file
output_csv = 'updated_links.csv' 
df.to_csv(output_csv, index=False)

print(f"Updated CSV saved as {output_csv}")





# load in csv

# loop through csv to get urls


# pick out class "text-center profile-image-wrapper"

html_page = requests.get('http://books.toscrape.com/')
soup = BeautifulSoup(html_page.content, 'html.parser')
warning = soup.find('div', class_="alert alert-warning")
book_container = warning.nextSibling.nextSibling