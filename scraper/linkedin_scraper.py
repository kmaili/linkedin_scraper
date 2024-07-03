# linkedin_scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import time
import random
import pandas as pd
from datetime import datetime
from config import USERNAME, PASSWORD, LINKEDIN_URL
from .constants import SCROLL_PAUSE_TIME
from .utils import convert_abbreviated_to_number, get_text, get_media_info, get_comment_replies
import re
class LinkedInScraper:
    def __init__(self):
        self.driver = self.initialize_driver()
        self.posts_data = []

    def initialize_driver(self):
        try:
            chrome_options = Options()
            return webdriver.Chrome(options=chrome_options)
            # selenium_grid_url = 'http://54.36.177.119:4432'
            # desired_cap = {
            #     'browserName': 'chrome',
            #     'remote': selenium_grid_url
            # }
            
            # return webdriver.Remote(
            #     command_executor=selenium_grid_url,
            #     options=Options()
            # )
        except Exception as e:
            print(f"Error initializing WebDriver: {e}")
            return None

    def login(self):
        try:
            self.driver.get("https://www.linkedin.com/login")
            self.driver.find_element(By.ID, "username").send_keys(USERNAME)
            self.driver.find_element(By.ID, "password").send_keys(PASSWORD)
            self.driver.find_element(By.ID, "password").submit()
            time.sleep(random.uniform(15, 25))
        except Exception as e:
            print(f"Error logging in: {e}")

    def navigate_to_posts_page(self):
        try:
            self.driver.get(LINKEDIN_URL)
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "feed-shared-update-v2")))
            time.sleep(random.uniform(3, 6))
        except Exception as e:
            print(f"Error navigating to the posts page: {e}")

    def scroll_page(self):
        try:
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            no_change_scrolls = 0

            while True:
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
                time.sleep(SCROLL_PAUSE_TIME)

                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    no_change_scrolls += 1
                    if no_change_scrolls > 2:
                        break
                else:
                    no_change_scrolls = 0
                    last_height = new_height
        except Exception as e:
            print(f"Error during scrolling: {e}")

    def extract_posts(self):
        try:
            source_page = self.driver.page_source
            linkedin_soup = bs(source_page.encode("utf-8"), "html.parser")
            posts = self.driver.find_elements(By.CSS_SELECTOR, "[data-view-name='feed-full-update']")
            previousLen = 0

            for post in posts:
                self.click_voir_plus(post)
                time.sleep(random.uniform(2, 5))
                soup = bs(post.get_attribute('outerHTML'), 'html.parser')
                post_text = get_text(soup, "div", {"class": "feed-shared-update-v2__description-wrapper"})
                media_link, media_type = get_media_info(soup)
                
                try:
                    reaction_count = soup.find("span", {"class":"social-details-social-counts__reactions-count"}).text.strip().split("\\", 1)[0]
                    print("reaction: ",reaction_count)
                except Exception as e:
                    print(f"Post has no reactions or error extracting reactions: {e}")
                    reaction_count = 0

                try:
                    share_count = soup.find("span", text=re.compile("republications")).text.strip().split('\\', 1)[0]
                    print("repub: ",share_count)
                    #share_count = convert_abbreviated_to_number(share_count.split()[0])
                except Exception as e:
                    print(f"Post has no shares or error extracting shares count: {e}")
                    share_count = 0

                post_comments = self.extract_comments_from_post(post, previousLen)
                previousLen += len(post_comments)

                self.posts_data.append({
                    "Text": post_text,
                    "MediaLink": media_link,
                    "MediaType": media_type,
                    "ReactionsCount": reaction_count,
                    "SharesCount": share_count,
                    "Comments": post_comments
                })
        except Exception as e:
            print(f"Error processing posts: {e}")

    def extract_comments_from_post(self, post, previousLen):
        try:
            buttons = post.find_elements(By.TAG_NAME, 'button')
            for button in buttons:
                aria_label = button.get_attribute('aria-label')
                if aria_label and aria_label == 'Commenter':
                    menu_button = button
                    self.driver.execute_script("arguments[0].click();", menu_button)
                    time.sleep(random.uniform(2, 5))
                    break
        except Exception as e:
            print(f"Error clicking 'Commenter' button: {e}")

        while True:
            try:
                buttons = post.find_elements(By.TAG_NAME, 'button')
                if len(buttons) == 0:
                    print("no show more found")
                    break
                for button in buttons:
                    className = button.get_attribute('class')
                    if className and re.search('comments-comments-list__load-more-comments-button', className):
                        more_comments_btn = button
                        self.driver.execute_script("arguments[0].click();", more_comments_btn)
                        time.sleep(random.uniform(3, 6))
                        break
                else:
                    break
            except Exception as e:
                print(f"Error loading more comments: {e}")
                break

        try:
            comments_soup = bs(self.driver.page_source.encode("utf-8"), "html.parser")
            all_comments_articles = comments_soup.find_all("article", {"class":"comments-comments-list__comment-item"})
            post_comments = []
            for index in range(previousLen, len(all_comments_articles)):
                main_comment = all_comments_articles[index].find("span", {"class":"comments-comment-item__main-content"})
                replies = get_comment_replies(all_comments_articles[index])
                post_comments.append({'comment': main_comment.find("span").text, 'replies': replies})
            return post_comments
        except Exception as e:
            print(f"Error extracting comments from post: {e}")
            return []

    def click_voir_plus(self, post):
        try:
            buttons = post.find_elements(By.TAG_NAME, 'button')
            for button in buttons:
                aria_label = button.get_attribute('aria-label')
                if aria_label and aria_label == 'voir plus, affiche du contenu déjà détecté par les lecteurs de l’écran':
                    show_more_button = button
                    self.driver.execute_script("arguments[0].click();", show_more_button)
                    time.sleep(random.uniform(2, 5))
                    break
        except Exception as e:
            print(f"Error clicking 'voir plus' button: {e}")

    def save_data(self):
        try:
            df = pd.DataFrame(self.posts_data)
            today = datetime.today().strftime('%Y-%m-%d')
            json_data = df.to_json(orient='records')
            with open(f'data/linked_posts_{today}.json', 'w') as file:
                file.write(json_data)
            df.to_csv(f"data/linkedin_posts_{today}.csv", index=False)
            print("Data saved to JSON and CSV successfully!")
        except Exception as e:
            print(f"Error saving data: {e}")

    def close_browser(self):
        try:
            self.driver.quit()
        except Exception as e:
            print(f"Error closing the browser: {e}")
