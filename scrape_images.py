from bs4 import BeautifulSoup
import requests

# load in csv

# loop through csv to get urls


# pick out class "text-center profile-image-wrapper"

html_page = requests.get('http://books.toscrape.com/')
soup = BeautifulSoup(html_page.content, 'html.parser')
warning = soup.find('div', class_="alert alert-warning")
book_container = warning.nextSibling.nextSibling