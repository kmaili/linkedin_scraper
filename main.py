# main.py
import time
from scraper.linkedin_scraper import LinkedInScraper

def main():
    scraper = LinkedInScraper()
    scraper.login()
    time.sleep(15)
    # scraper.publication_exists(pub_link="https://www.linkedin.com/posts/aymen-kmaili-75851a1bb_rapport-activity-7204150308103479296-l6Jb/")
    # scraper.publication_exists(pub_link="https://www.linkedin.com/posts/aymen-kmaili-75851a1bb_rapport-activity-7204150308103479296-l6Jbc/")
    # s1 = scraper.get_user_info(user_id="aymen-kmaili-75851a1bb")
    # s2 = scraper.get_user_info(user_id="oussama-chaabene")
    # print(s1)
    # print(s2)
    
    # scraper.pseudo_exists(user_id="aymen-kmaili-75851a1bb")
    
    scraper.navigate_to_posts_page()
    scraper.scroll_page()
    scraper.extract_posts()
    scraper.save_data()
    scraper.close_browser()

if __name__ == "__main__":
    main()
