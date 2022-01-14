# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():

    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    # Run all scraping functions and store results in a dictionary
    news_title, news_paragraph = mars_news(browser)
    data = {
        'news_title' : news_title,
        'news_paragraph' : news_paragraph,
        'featured_image' : featured_image(browser),
        'facts' : mars_facts(),
        'hemispheres' : hemispheres(browser),
        'last_modified' : dt.datetime.now()
    }
    
    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    # Visit the Mars news site
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')

        slide_elem.find('div', class_='content_title')

        # Use the parent element to find the first a tag and save it as `news_title`
        news_title = slide_elem.find('div', class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

# ## JPL Space Images Featured Image

def featured_image(browser):

    # Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        # find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    
    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url

# ## Mars Facts

def mars_facts():
    #use 'read_html' to scrape the facts table into a dataframe
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    return df.to_html(classes = ['table table-bordered table-striped table-hover'])

def hemispheres(browser):
    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    try:
        # 3. Write code to retrieve the image urls and titles for each hemisphere.
        num_items = len(browser.find_by_css('div[class = "description"]'))

        # Loop over the number of hemispheres
        for ii in range(num_items):

            # wait for loading
            browser.is_element_present_by_tag('h3', wait_time = 10)

            # scrape the hemispheres
            items = browser.find_by_css('div[class = "description"]')
            item = items[ii]
            
            # get the title
            title = item.find_by_css('h3').text

            # go to the specific hemisphere webpage
            item.find_by_css('a').click()

            # get the image url
            browser.is_element_present_by_text('Download', wait_time = 10)
            img_url = browser.find_by_text('Sample')['href']

            # create the output dict
            hemisphere = {
                'img_url' : img_url,
                'title' : title
            }
            hemisphere_image_urls.append(hemisphere)
            browser.back()
            
    except BaseException:
        return None

    return hemisphere_image_urls

if __name__ == '__main__':
    # If running as script, print scraped data
    print(scrape_all())