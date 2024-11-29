import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def scrapename(url):
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto(url)
    await page.wait_for_selector(".name")
    product_name = await page.query_selector(".name")
    product_name_text = await product_name.inner_text() if product_name else "No name found"
    await browser.close()
    await playwright.stop()
    return product_name_text

async def scrape_doorzo(soup, marketplace, url):
    try:
        app_main_div = soup.find('div', class_='app-main')
        product_image_url = None
        if app_main_div:
            img_tag = app_main_div.find('img')
            if img_tag:
                product_image_url = img_tag.get('src') or img_tag.get('data-src')

        print(f"Product image found: {product_image_url or 'No image found'}")

        print("Looking for product name...")
        if marketplace == 'street-detail':
            product_name = await scrapename(url)
        else:
            product_name = "No name found"
            name_box = soup.find('div', class_='name-box')
            if name_box:
                name_tag = name_box.find('h1', class_='name')
                if name_tag:
                    product_name = name_tag.get_text(strip=True)

        print(f"Product name found: {product_name}")

        print("Looking for price...")
        price = "No price found, could be sold out!"
        price_box = soup.find('div', class_='price-box')
        if price_box:
            price_com = price_box.find('p', class_='price-com')
            if price_com:
                price = price_com.get_text(strip=True)
        print(f"Price found: {price}")

        print("Looking for description...")
        if marketplace == 'street-detail':
            print("Looking for description for amazon...")
            description_div = soup.find('div', class_='el-tab-pane')
            if description_div:
                description = description_div.get_text(separator=" ",strip=True)
                if description:
                    print(f"Description found: {description}")
                else:
                    print("Description not found.")
            else:
                print("Error: Amazon description not found.")
        else:
            description = "No description found"
            tab_box = soup.find('div', class_='tab-box')
            if tab_box:
                content = tab_box.find('div', class_='el-tabs__content')
                if content:
                    description_div = content.find('div', class_='html')
                    if description_div:
                        description = description_div.get_text(strip=True)
            print(f"Description found: {description}")

        # Return the extracted data
        return {
            "product_name": product_name,
            "price": price,
            "product_image_url": product_image_url,
            "description": description,
            "marketplace": marketplace,
        }

    except AttributeError as e:
        print(f"Error while scraping: {e}")
        return f"Error while scraping: {e}"

async def scrape_product(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    print("Fetching the URL...")
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status Code: {response.status_code}")
        return "Couldn't retrieve the page."

    print("Parsing the page content...")
    soup = BeautifulSoup(response.content, 'html.parser')

    app_main_div = soup.find('div', class_='app-main')
    if not app_main_div:
        print("'app-main' div not found!")
        return "'app-main' div not found!"

    marketplace = None
    for div in app_main_div.find_all('div', recursive=False):
        classes = div.get('class', [])
        if classes and classes[0] not in ['app-main', 'main']:
            marketplace = classes[0]
            break

    if not marketplace:
        print("Marketplace class not found.")
        return "Marketplace class not found."

    print(f"Marketplace found: {marketplace}")

    if "doorzo.com" in url:
        print("Scraping product from Doorzo...")
        return await scrape_doorzo(soup, marketplace, url)
    else:
        print("Unsupported marketplace.")
        return "Unsupported marketplace."
