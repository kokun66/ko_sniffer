from argparse import ArgumentParser
import requests
from bs4 import BeautifulSoup
import csv
import queue
import re
import time
import random
import logging
import os

class KoCrawler:
    def __init__(self, 
                 data_dir: str=None,
                 log_file: str=None,
                 verbose_level: int=51,
                 seed_url: str=None,
                 url_limit: int=0):
        
        # Create a custom logger
        self.logger = logging.getLogger('ko_crawler')
        self.logger.setLevel(verbose_level)

        # Create handlers
        self.console_handler = logging.StreamHandler()
        #console_handler.setLevel(args.verbose_level)
        self.console_handler.setLevel(logging.CRITICAL + 1)

        self.logfile_handler = logging.FileHandler(log_file, mode='w')
        self.logfile_handler.setLevel(verbose_level)

        # Create a formatter and set it for both handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.console_handler.setFormatter(formatter)
        self.logfile_handler.setFormatter(formatter)

        self.logger.addHandler(self.console_handler)
        self.logger.addHandler(self.logfile_handler)

        self.seed_url = seed_url
        self.url_limit = url_limit

        self.data_dir = data_dir
        self.create_data_dir(data_dir)

        # Log messages
        self.logger.info(f"ko_sniffer started from {self.seed_url}, url_limit={self.url_limit}, saved at {self.data_dir}")

        
            
    def __del__(self):
        #
        #self.logger.info(f"Done, total_visited_urls={len(visited_urls)}, max_ulrs={urls_limit}")
        # Close the handler
        self.logfile_handler.close()
        self.logger.removeHandler(logfile_handler)

    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        return f"{self.__class__.__name__}"


    # Function to create directory if not exist
    def create_data_dir(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    '''return empty string if failed'''
    def get_html(self, url):     
        try: 
            return requests.get(url).content 
        except Exception as e: 
            print(e) 
            return ''
        

    def crawl_page(self, soup, url, visited_urls, que_urls, log): 
        link_elements = soup.select("a[href]")
        for link_element in link_elements:
            curr_url = link_element['href']
            log.info(f"crawl: {curr_url}")
            if curr_url not in visited_urls and curr_url not in [item[1] for item in que_urls.queue]:                
                if re.match(r"^https://scrapingcourse\.com/shop/page/\d+/?$", url):
                    priority_score = 0.5
                else:
                    priority_score = 1.0
                que_urls.put((priority_score, url))
            time.sleep(0.5)

    def scrape_page(self, soup, log): 
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
            log.info(f"found {len(felix_image)}  images with Felix")


''''''        
def main(args):   

    ko_crawler = KoCrawler(
                        data_dir=args.data_dir,
                        log_file=args.log_file, 
                        verbose_level=args.verbose_level, 
                        seed_url=args.seed_url,
                        url_limit=args.max_urls)

    
    

    # initialize the list of discovered urls
    # with the first page to visit
    q_urls = queue.PriorityQueue()
    q_urls.put((0.5, seed_url))
    visited_urls = []
    
    while not q_urls.empty() and len(visited_urls) < urls_limit:

        current_pri, current_url = q_urls.get()
        
        curr_html = get_html(current_url)
        if ''==curr_html:
            logger.info(f"get {current_url} failed.")
            break

        soup = BeautifulSoup(curr_html, "html.parser")
        visited_urls.append(current_url)
        logger.info(f"url[{len(visited_urls)}]: {current_url}, queued: {q_urls.qsize()}")

        #
        crawl_page(soup, current_url, visited_urls, q_urls, logger)
    
        #
        scrape_page(soup, logger)

        #
        time.sleep(random.uniform(1, 2))





'''
'''
def parse_args():
    parser = ArgumentParser()

    #parser.add_argument('img', help='Image file')
    parser.add_argument('--seed-url', default="https://www.scrapingcourse.com/ecommerce/", help='starting url')
    parser.add_argument('--max-urls', type=int, default=50, help='')
    parser.add_argument('--verbose-level', type=int, default=20, help='logging level')
    parser.add_argument('--log-file', default='ko_logging.txt', help='Path to save logging')
    parser.add_argument('--data-dir', default='data', help='Path to save data')

    args = parser.parse_args()
    return args


'''
'''
if __name__ == '__main__':
    args = parse_args()
    main(args)
