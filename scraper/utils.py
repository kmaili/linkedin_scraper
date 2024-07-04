# utils.py
from bs4 import BeautifulSoup
import re

def convert_abbreviated_to_number(s):
    try:
        if 'K' in s:
            return int(float(s.replace('K', '')) * 1000)
        elif 'M' in s:
            return int(float(s.replace('M', '')) * 1000000)
        else:
            return int(s)
    except Exception as e:
        print(f"Error converting abbreviated number: {e}")
        return 0

def get_text(container, selector, attributes):
    try:
        element = container.find(selector, attributes)
        if element:
            return element.text.strip()
    except Exception as e:
        print(f"Post has no text or error extracting text: {e}")
    return ""

def get_media_info(container):
    media_info = [("div", {"class": "update-components-document__container"}, "pdf_images"),
                  ("div", {"class": "update-components-video"}, "Video"),
                  ("div", {"class": "update-components-linkedin-video"}, "Video"),
                  ("div", {"class": "update-components-image"}, "Image")]
    
    for selector, attrs, media_type in media_info:
        try:
            element = container.find(selector, attrs)
            if element:
                link = element.find('img' if media_type == 'Image' else 'video')
                return link['src' if media_type == 'Image' else 'poster'] if link else "None", media_type
        except Exception as e:
            print(f"Error extracting media info: {e}")
    return "None", "Unknown"

def get_comment_replies(comment):
    try:
        replies_div = comment.find("div", {"class":"comments-replies-list"})
        if(not replies_div):
            return None
        all_replies_articles = replies_div.find_all("article", {"class":"comments-comment-entity--reply"})
        comment_replies = []
        for article in all_replies_articles:
            main_comment = article.find("span", {"class":"comments-comment-item__main-content"})
            comment_replies.append(main_comment.find("span").text)
        return comment_replies
    except Exception as e:
        print(f"Error getting comment replies: {e}")
        return None
