import requests, random, urllib.parse, pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from bs4 import BeautifulSoup as bs
from datetime import datetime


def scrape(url):
    def get_soups(url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers)

        sleep(random.randint(1, 5))

        soup = bs(response.content, "lxml")

        yield soup

        next_page_node = soup.select_one("a#pnnext")

        if next_page_node is None:
            return None

        base = "https://www.google.com"
        remaining = next_page_node["href"]
        next_page_url = urllib.parse.urljoin(base, remaining)

        yield from get_soups(next_page_url)

    urls = []
    soups = get_soups(url)

    for soup in soups:
        results = soup.select(".WlydOe")

        for result in results:
            link = result["href"]
            urls.append(link)

    return urls


# Dictionary of the hostnames of the news sources
source_host_dic = {
    "bbc": "bbc.com",
    "cnn": "cnn.com",
    "thestandard": "thestandard.com.hk",
    "rthk": "news.rthk.hk",
    "hkfp": "hongkongfp.com",
    "yomiuri": "yomiuri.co.jp",
    "asahi": "asahi.com/ajw/",
    "mainichi": "mainichi.jp",
    "japantimes": "japantimes.co.jp",
    "koreaherald": "koreaherald.com",
    "koreatimes": "www.koreatimes.co.kr",
    "koreajoongangdaily": "koreajoongangdaily.joins.com",
    "theguardian": "theguardian.com",
    "dailymail": "dailymail.co.uk",
    "foxnews": "foxnews.com",
    "news.com.au": "news.com.au",
    "abc": "abc.net.au",
    "straitstimes": "www.straitstimes.com",
    "todayonline": "todayonline.com",
}

# Main function
def urls_scraping(keyword: str, from_date: str, to_date: str) -> None:
    # Create a list to store the URLs of the news articles
    urls = []

    # Append the "site:" operator with the first hostname "bbc.com" to the keyword
    first_site = list(source_host_dic.values())[0]
    new_keyword = f"{keyword} site:{first_site}"

    # Create a Chrome browser window
    driver = webdriver.Chrome()
    """     
    Set the implicit waiting time to 60 seconds, which means the browser will wait for 60 seconds
    before throwing an exception to ensure no errors occur when the network speed is slow.  
    """
    driver.implicitly_wait(60)

    # Navigate to the Google Search page
    driver.get(
        "https://www.google.com/webhp?as_q=&as_epq=&as_oq=&as_eq=&as_nlo=&as_nhi=&lr=lang_en&cr=&as_qdr=all&as_sitesearch=&as_occt=any&safe=images&as_filetype=&tbs="
    )

    # Enter the keyword into the search box and submit the search
    search_box = driver.find_element("name", "q")
    search_box.send_keys(new_keyword)
    search_box.submit()

    # Select the "News" tag from the navigation bar
    news_button = driver.find_element(
        "xpath", '//*[@id="hdtb-msb"]/div[1]/div/div[2]/a'
    )
    news_button.click()

    # Click the "Tools" button to expand the search options
    tools_button = driver.find_element("xpath", '//*[@id="tn_1"]/span[2]')
    tools_button.click()

    # Open the date range filter
    custom_range_button = driver.find_element(
        "xpath", '//*[@id="lb"]/div/g-menu/g-menu-item[8]'
    )
    custom_range_button.click()

    # Enter the start date and end date
    from_box = driver.find_element("xpath", '//*[@id="OouJcb"]')
    from_box.send_keys(from_date)
    to_box = driver.find_element("xpath", '//*[@id="rzG2be"]')
    to_box.send_keys(to_date)
    # Press the Enter key to submit the search
    to_box.send_keys(Keys.ENTER)

    # Get the current URL
    url = driver.current_url
    # Initialize the variable "source" to "bbc", used to identify the news media of the URL
    source = list(source_host_dic.keys())[0]
    print(f"Scraping {source} urls from {url} ...")

    # Call the function "scrape" to scrape the URLs
    urls = scrape(url)
    print(f"{len(urls)} urls were scraped.\n")

    # Create a data frame to store the scraped URLs
    df = pd.DataFrame(
        data={
            "Source": source,
            "URL": urls,
            "Scraped": 0,
            "Skipped": 0,
        }
    )

    # Loop through the remaining news media in the dictionary "source_host_dic"
    for key, site in zip(
        list(source_host_dic.keys())[1:], list(source_host_dic.values())[1:]
    ):
        # Append the "site:" operator with the hostname to the keyword
        new_keyword = f"{keyword} site:{site}"

        # Find the search box and clear the text in the search box
        search_box = driver.find_element("name", "q")
        search_box.clear()

        # Enter the keyword into the search box and submit the search
        search_box.send_keys(new_keyword)
        search_box.submit()

        # Get the current URL
        url = driver.current_url
        # Update the variable "source" to the current handling of news media
        source = key
        print(f"Scraping {source} urls from {url} ...")

        # Call the function "scrape" to scrape the URLs
        urls = scrape(url)
        print(f"{len(urls)} urls were scraped.\n")

        # Append the scraped URLs to the DataFrame
        data = {
            "Source": source,
            "URL": urls,
            "Scraped": 0,
            "Skipped": 0,
        }
        df = pd.concat([df, pd.DataFrame(data=data)])

    # Close the Chrome browser window
    driver.quit()

    # Append the scraped URLs to the CSV file
    df.to_csv("urls.csv", mode="a", index=False, header=False)

    # Write a log entry with the current date
    with open("log.txt", "r+") as f:
        content = f.read()
        # Set the file pointer to the beginning of the file, which means the new content will be written to the first line
        f.seek(0, 0)
        today = datetime.today().strftime("%m/%d/%Y")
        f.write(f"{today}\n" + content)

    return None
