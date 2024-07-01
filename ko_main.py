from argparse import ArgumentParser
import requests
from bs4 import BeautifulSoup
import csv
import queue
import re
import time
import random
import logging


'''return empty string if failed'''
def get_html(url):     
    try: 
        return requests.get(url).content 
    except Exception as e: 
        print(e) 
        return ''
    

def crawl_page(soup, url, visited_urls, que_urls, is_verbose): 
    link_elements = soup.select("a[href]")
    for link_element in link_elements:
        curr_url = link_element['href']
        if is_verbose:
            print(f"crawl: {curr_url}")
        if curr_url not in visited_urls and curr_url not in [item[1] for item in que_urls.queue]:                
            if re.match(r"^https://scrapingcourse\.com/shop/page/\d+/?$", url):
                priority_score = 0.5
            else:
                priority_score = 1.0
            que_urls.put((priority_score, url))
        time.sleep(0.5)

def scrape_page(soup, is_verbose): 
    # Filter images with names including "Felix"
    felix_images = []
    # Find all image tags
    img_tags = soup.find_all('img')    
    for img in img_tags:
        # Check if the 'src' attribute contains "Felix"
        if 'src' in img.attrs and 'Felix' in img.attrs['src']:
            felix_images.append(img.attrs['src'])
        # Check if the 'alt' attribute contains "Felix"
        elif 'alt' in img.attrs and 'Felix' in img.attrs['alt']:
            felix_images.append(img.attrs['alt'])

    if(len(felix_images)):
        if is_verbose:
            print(f"found {len(felix_image)}  images with Felix")


''''''        
def main(args):
    is_verbose=args.verbose_level
    urls_limit=args.max_urls


    # Create a custom logger
    logger = logging.getLogger('ko_logger')
    logger.setLevel(args.verbose_level)

    # Create handlers
    console_handler = logging.StreamHandler()
    #console_handler.setLevel(args.verbose_level)
    console_handler.setLevel(logging.CRITICAL + 1)

    file_handler = logging.FileHandler(args.log_file)
    file_handler.setLevel(args.verbose_level)

    # Create a formatter and set it for both handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)


    # Log messages
    logger.info('This is an info message')
    

    # initialize the list of discovered urls
    # with the first page to visit
    q_urls = queue.PriorityQueue()
    q_urls.put((0.5, "https://www.scrapingcourse.com/ecommerce/"))
    visited_urls = []
    
    while not q_urls.empty() and len(visited_urls) < urls_limit:

        current_pri, current_url = q_urls.get()
        
        curr_html = get_html(current_url)
        if ''==curr_html:
            break

        soup = BeautifulSoup(curr_html, "html.parser")
        visited_urls.append(current_url)
        if is_verbose:
            print(f"url[{len(visited_urls)}]: {current_url}, queued: {q_urls.qsize()}")

        #
        crawl_page(soup, current_url, visited_urls, q_urls, is_verbose)
    
        #
        scrape_page(soup, is_verbose)

        #
        time.sleep(random.uniform(1, 2))


    if is_verbose:
        print(f"Done, total_visited_urls={len(visited_urls)}, max_ulrs={urls_limit}")


'''
'''
def parse_args():
    parser = ArgumentParser()

    #parser.add_argument('img', help='Image file')
    parser.add_argument('--max-urls', type=int, default=50, help='')
    parser.add_argument('--verbose-level', type=int, default=20, help='logging level')
    parser.add_argument('--log-file', default='ko_logging.txt', help='Path to save logging')

    args = parser.parse_args()
    return args


'''
'''
if __name__ == '__main__':
    args = parse_args()
    main(args)
