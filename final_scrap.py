import requests
from bs4 import BeautifulSoup
import time  # Import the time module for adding delays
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager



import sys
import io

# Set the output encoding to UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Now print Unicode characters
print("Character: \u010d")  # This should work without errors
# Function to scrape the last page number
def scrape_pages_of_pagination_new(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76"
    }
    print(url)
    try:
        # Send a GET request to the URL
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404, 500)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find the Pagination_numbers__9OjwH element
    pagination_element = soup.find("li", class_="Pagination_numbers__9OjwH")
    
    if not pagination_element:
        print("Pagination element not found.")
        return None

    # Find all <span> elements within the pagination element
    span_elements = pagination_element.find_all("span", class_="Button_children__tDTVo")
    
    if not span_elements:
        print("No span elements found within the pagination element.")
        return None

    # Get the last <span> element's text
    last_span_value = span_elements[-1].text

    # Ensure the value is a number
    try:
        last_span_value = int(last_span_value)
    except ValueError:
        print(f"Last span value is not a number: {last_span_value}")
        return None

    print("Last span value:", last_span_value)
    return last_span_value



# Function to iterate through all pages and scrape product links
def iterate_through_pages(base_url):
    """
    Iterates through all pages of the search results and collects all product links.
    """
    # Remove the last character (page number) from the base URL
    base_url = base_url[:-1]
    print(base_url)
    # Get the total number of pages
    last_page_number = scrape_pages_of_pagination_new(f"{base_url}1")
    
    if last_page_number is None:
        print("Failed to determine the number of pages. Exiting.")
        return
    #last_page_number=1
    # Initialize an empty list to store all product links
    all_product_links = []
    last_page_number=5
    # Iterate through each page
    for page in range(1, last_page_number + 1):
        # Construct the URL for the current page
        page_url = f"{base_url}{page}"
        print(f"Processing page {page} of {last_page_number}...")
        
        # Call the function to scrape product links on the current page
        product_links = scrape_all_prods(page_url)
        
        # Append the links from this page to the global list
        if product_links:
            all_product_links.extend(product_links)
    
    # Print all collected links after all iterations
    print("All collected product links:", all_product_links)
    return all_product_links

def scrape_all_prods(page_url):
    """
    Scrapes all product links (href) on a given page and returns them as a list.
    Excludes links that contain 'https' or 'promocije'.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76"
    }
    
    try:
        # Send a GET request to the URL
        response = requests.get(page_url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404, 500)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None

    # Parse the HTML content
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Locate the parent div with the specified classes
    parent_div = soup.find("div", class_="Grid_col-lg-10__FPLVk Grid_col-xs__w58_v Grid_col-sm__DsLxt Grid_col-md__eg0dB")

    # Check if the parent div is found
    if parent_div:
        # Find the first direct child div inside the parent div
        first_child_div = parent_div.find("div", recursive=False)
        
        if first_child_div:
            # Find all direct child elements (section, div, etc.) inside the first child div
            child_elements = first_child_div.find_all(recursive=False)
            
            # Check if there are at least 3 child elements
            if len(child_elements) >= 3:
                # Target the third child element (index 2 because Python uses zero-based indexing)
                target_div = child_elements[2]
                
                # Ensure the third child is a div (optional, for safety)
                if target_div.name == "div":
                    # Find all <a> tags inside the target div that have an href attribute
                    product_links = target_div.find_all("a", href=True)
                    
                    # Extract the href attributes from the <a> tags
                    product_hrefs = [link["href"] for link in product_links]
                    
                    # Remove duplicates by converting the list to a set and back to a list
                    unique_links = list(set(product_hrefs))
                    
                    # Filter out links that contain 'https' or 'promocije'
                    filtered_links = [
                        link for link in unique_links
                        if 'https' not in link and 'promocije' not in link
                    ]
                    
                    # Print the filtered links for debugging
                    print("Filtered links:")
                    print(filtered_links)
                    
                    # Return the list of filtered product links
                    return filtered_links
                else:
                    print("The third child is not a div.")
            else:
                print("The first child div does not have at least 3 child elements.")
        else:
            print("First child div not found inside the parent div.")
    else:
        print("Parent div not found.")
    
    # Return an empty list if no links are found
    return []

""" def scrape_product_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76"
    }
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

# Extract product name
    product_name_element = soup.find("h1", class_="AdViewInfo_name__VIhrl")
    print(product_name_element)
    product_name = product_name_element.text.strip() if product_name_element else "N/A"
    # Extract price
    price_element = soup.find("h2", class_="AdViewInfo_price__J_NcC")
    price = price_element.text.strip() if price_element else "N/A"

    # Extract location (inside a <span> tag)
    location_element = soup.find("span", class_="UserSummary_userLocation__FTK_2")
    location = location_element.text.strip() if location_element else "N/A"

    # Extract image URL
    image_tag = soup.find("img", class_="GallerySlideItem_imageGalleryImage__UlbIb")
    image_url = image_tag["src"] if image_tag else "N/A"

    # Return structured data
    return {
        "product_name": product_name,
        "price": price,
        "location": location,
        "product_url": url,
        "image_url": image_url
    } """


def scrape_product_page(product_url):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76"
    }

    
    response = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

# Extract product name
    """     product_name_element = soup.find("h1", class_="AdViewInfo_name__VIhrl")
    #print(product_name_element)
    product_name = product_name_element.text.strip() if product_name_element else "N/A" """
    # Extract product name
    product_name_element = soup.find("h1", class_="AdViewInfo_name__VIhrl")
    if product_name_element:
        product_name = product_name_element.text.strip()
        product_name = product_name.encode('utf-8', errors='ignore').decode('utf-8')
    else:
        product_name = "N/A"
    # Extract price
    price_element = soup.find("h2", class_="AdViewInfo_price__J_NcC")
    price = price_element.text.strip() if price_element else "N/A"

    # Extract location (inside a <span> tag)
    location_element = soup.find("span", class_="UserSummary_userLocation__FTK_2")
    location = location_element.text.strip() if location_element else "N/A"

    # Extract image URL
    image_tag = soup.find("img", class_="GallerySlideItem_imageGalleryImage__UlbIb")
    image_url = image_tag["src"] if image_tag else "N/A"

    # Return structured data
    return {
        "product_name": product_name,
        "price": price,
        "location": location,
        "product_url": product_url,
        "image_url": image_url
    }

# Function to iterate through all links and scrape product details
def scrape_all_product_pages(all_links):
    """
    Iterates through all product links, scrapes each product page, and stores the results in a DataFrame.
    """
    # Initialize an empty list to store all product details
    all_product_details = []
    product_id_counter = 1
    # Iterate through each link
    for link in all_links:
        # Construct the full URL
        full_url = f'https://www.kupujemprodajem.com{link}'
        print(f"Scraping product page: {full_url}")
        
        # Scrape the product page (assuming scrape_product_page is a valid function)
        product_details = scrape_product_page(full_url)
        print(transform_price(product_details['price']))
        # Apply transformation to the price
        
        transformed_price = transform_price(product_details['price'])
        #print(f"Transformed price for {product_details['product_name']}: {transformed_price}")

        # Now safely unpack the values
        if transformed_price is not None:
            transformed_price_value, transformed_currency = transformed_price
        else:
            # Handle the None case if transformation failed
            transformed_price_value, transformed_currency = 0, None
        
        # Update the product_details with the transformed price and currency
        product_details['price_value'] = transformed_price_value
        product_details['currency'] = transformed_currency
        product_details['product_id'] = product_id_counter
        print(product_details)
    # Increment the ID counter for the next product
        product_id_counter += 1
        print(product_id_counter)
        if product_details.get('product_name') is not None and product_details.get('image_url') is not None:# and product_details['product_id']<=6:
            # Append the updated product details to the list
            all_product_details.append(product_details)
        else:
            print(f"Skipping product due to missing product_name or image_url: {full_url}")
        #if(product_id_counter==6):
         #   break
        # Append the updated product details to the list
        #all_product_details.append(product_details)
        
        #print("Waiting for 10 seconds before the next request...")
        time.sleep(10)
    
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(all_product_details)
    
    # Print the DataFrame to verify the data
    print(df['price_value'])
    
    # Return the DataFrame
    return df
# Example usage
def transform_price(price):
    # Remove "Fiksno" from the price string
    price = price.replace("Fiksno", "").strip()
    
    # Exclude "Kupujem" and return None in such cases
    if "Kupujem" in price:
        return None
    
    # If price is "Kontakt", return 0 as price and None for currency
    if "Kontakt" in price:
        return [0,None]
    
    # Initialize currency and price value variables
    currency = None
    price_value = None
    
    # Extract the currency and price value
    if "din" in price:
        currency = "din"
        price_value = price.replace("din", "").strip()
    elif "€" in price:
        currency = "eur"
        price_value = price.replace("€", "").strip()
    else:
        return None  # Return None if no known currency is found
    
    # Clean the price value and convert it to an integer
    try:
        # Convert price to float first in case of decimals with commas or periods
        price_value = float(price_value.replace(".", "").replace(",", "."))
        # Convert to integer after conversion
        price_value = int(price_value)
    except ValueError:
        return None  # Return None if conversion to integer fails
    
    # Return the transformed data in dictionary format
    if (price_value is None):
        price_value = 0 
    if (currency is None):
        currency = "No"         
    print(price_value,currency)        
    return  [price_value, currency]



def main():
    # Your script's logic here
    print("Running the main function!")
    base_url = "https://www.kupujemprodajem.com/pretraga?keywords=adidas%2046&keywordsScope=description&order=posted%20desc&prev_keywords=adidas%2046&page=1"
    all_links = iterate_through_pages(base_url)
    df = scrape_all_product_pages(all_links)

    # Optionally, save the DataFrame to a CSV file
    df.to_csv("product_details.csv", index=False)

if __name__ == "__main__":
    main()  # Call the main function