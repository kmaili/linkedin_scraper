# main.py
from scraper.linkedin_scraper import LinkedInScraper

def main():
    scraper = LinkedInScraper()
    scraper.login()
    scraper.navigate_to_posts_page()
    scraper.scroll_page()
    scraper.extract_posts()
    scraper.save_data()
    scraper.close_browser()

if __name__ == "__main__":
    main()
