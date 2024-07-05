from argparse import ArgumentParser
import requests
from bs4 import BeautifulSoup
from PIL import Image
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
                 urls_limit: int=0):
        
        # Create a custom logger
        self.logger = logging.getLogger('ko_sniffer')
        self.logger.setLevel(verbose_level)

        # Create handlers
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(args.verbose_level)
        #self.console_handler.setLevel(logging.CRITICAL + 1) # if want to turn it off

        self.logfile_handler = logging.FileHandler(log_file, mode='w')
        self.logfile_handler.setLevel(verbose_level)

        # Create a formatter and set it for both handlers
        #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.console_handler.setFormatter(formatter)
        self.logfile_handler.setFormatter(formatter)

        self.logger.addHandler(self.console_handler)
        self.logger.addHandler(self.logfile_handler)

        self.data_dir = data_dir
        self.create_data_dir(data_dir)

        self.urls_limit = urls_limit
        self.url_visited = 0

        # Log messages
        self.logger.info(f"started  with url_limit={self.urls_limit}, saved at {self.data_dir}")

        
            
    def __del__(self):
        self.logger.info(f"Done, total_visited_urls={self.url_visited}, max_ulrs={self.urls_limit}")
        # Close the handler
        self.logfile_handler.close()
        self.logger.removeHandler(self.logfile_handler)

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
        
    def scrape_and_save_images(self, seed_url: str=None, search_name: str=None): 
        # Fetch the web page
        response = requests.get(seed_url)

        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all image tags
        img_tags = soup.find_all('img')
        
        # Extract image URLs
        img_urls = [img['src'] for img in img_tags if 'src' in img.attrs]
        
        self.logger.info(f"total image urls: {len(img_urls)}")

        # Filter and save images with "felix" in the name
        for img_idx, img_url in enumerate(img_urls, start=1):        
            self.logger.info(f"[{img_idx}]: {img_url}")
            if search_name in img_url.lower():
                try:
                    # Download image
                    img_response = requests.get(img_url)
                    img = Image.open(io.BytesIO(img_response.content))
                    
                    # Generate filename
                    filename = os.path.join(self.data_dir, os.path.basename(img_url))
                    
                    # Save image
                    img.save(filename)
                    print(f"Saved: {filename}")
                except Exception as e:
                    print(f"Error saving {img_url}: {str(e)}")



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

    
''''''        
def main(args):   

    ko_crawler = KoCrawler(
                        data_dir=args.data_dir,
                        log_file=args.log_file, 
                        verbose_level=args.verbose_level, 
                        urls_limit=args.max_urls)

    ko_crawler.scrape_and_save_images(args.seed_url, args.search_name)    
    





'''
'''
def parse_args():
    parser = ArgumentParser()

    #parser.add_argument('img', help='Image file')
    parser.add_argument('--seed-url', default="https://www.scrapingcourse.com/ecommerce/", help='starting url')
    parser.add_argument('--search-name', default="felix", help='the pattern to match')
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
