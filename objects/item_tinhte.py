import os
import time
import re
import json

from bs4 import BeautifulSoup
import hashlib
from utils.utils import setup_selenium_firefox
from objects.item import Item
from selenium.webdriver.common.by import By


class ItemTinhTe(Item):

    def __init__(self, data_packet: dict, keyword: str, path_save_data):
        super(ItemTinhTe, self).__init__(data_packet)
        self.url = data_packet["url"]
        self.id = self.item_id
        self.keyword = keyword
        self.path_save_data = path_save_data
        self.number_page_comment = 1
        self.driver = None
        self.title = None
        self.content = None
        self.comments = None
        self.number_comment = 0

    @property
    def item_id(self):
        return hashlib.md5(str(self.url).encode("utf-8")).hexdigest()

    def access_website(self):
        self.driver = setup_selenium_firefox()
        res = ""
        for _ in range(5):
            try:
                res = ""
                self.driver.get(self.url)
                break
            except:
                res = None
                continue
        if res is None:
            self.driver.close()
            return None
        time.sleep(3)
        return self.parse_html()

    @staticmethod
    def get_title(soup):
        title_tag = soup.find("div", class_="jsx-3147581474 thread-title")
        if title_tag is not None:
            title = title_tag.text
        else:
            title = ""
        return title

    def parse_html(self):
        return BeautifulSoup(self.driver.page_source, "lxml")

    @staticmethod
    def get_content(soup):
        list_index = []
        list_text = []
        content_tag = soup.find("article", class_="jsx-3147581474 content")
        if content_tag is None:
            return None
        content = content_tag.get_text(separator=" ")
        # NORMALIZE
        content = re.sub(r"(\n\s*)+", "\n", content)
        content = re.sub(r"( )+", " ", content)
        # for _ in range(20):
        #     content = content.replace("\n\n", "\n")
        # GET MINI TITLE CONTENT
        list_title_tag = soup.findAll("h2", class_="TinhteMods_HeadingTag TinhteMods_HeadingTagH2")
        if not len(list_title_tag):
            list_title_tag = soup.findAll("h3", class_="TinhteMods_HeadingTag TinhteMods_HeadingTagH3")
        if not len(list_title_tag):
            return [content]
        list_title = [each.text for each in list_title_tag]
        list_title = [each for each in list_title if len(each)]
        for title in list_title:
            if re.search(r"\n\s*" + title, content) is not None:
                list_index.append(re.search(r"\n\s*" + title, content).span())
        if not len(list_index):
            return [content]
        start = 0
        end = list_index[0][0]
        list_text.append(content[start:end])
        for i in range(len(list_index)):
            if i == (len(list_index)-1):
                start = list_index[i][0]
                end = -1
            else:
                start = list_index[i][0]
                end = list_index[i+1][0]
            list_text.append(content[start:end])
        return list_text

    @staticmethod
    def get_number_page_comment(soup):
        box = soup.find("div", class_="jsx-2305813501")
        if box is None:
            return 1
        list_page = box.findAll("a", class_="jsx-2305813501 page")
        if not len(list_page):
            return 1
        number_page = int(list_page[-1].text)
        return number_page

    @staticmethod
    def format_url(url):
        if re.search("[/][?]", url) is not None:
            start, end = re.search("[/][?]", url).span()
            url = url[:start]
        if re.search("[/]$", url) is not None:
            url = url[:-1]
        return url

    def click_load_more(self):
        for _ in range(3):
            list_load = self.driver.find_elements(By.CLASS_NAME, value="jsx-691990575.thread-comments__load-more")
            if not len(list_load):
                break
            for each in list_load:
                each.click()
                time.sleep(1)
            time.sleep(2)

    def get_all_comment(self):
        list_all_dialogue = []
        url_original = self.format_url(self.url)
        self.click_load_more()
        soup = self.parse_html()
        list_box_comment = soup.findAll("div", class_="jsx-691990575 thread-comment__wrapper")
        for box in list_box_comment:
            list_all_dialogue.append(self.get_dialogue(box))
        if self.number_page_comment == 1:
            self.comments = list_all_dialogue
            return
        for page in range(2, self.number_page_comment+1):
            url = url_original + "/page-" + str(page)
            list_all_dialogue = list_all_dialogue + self.get_comment_in_page(url)
            self.comments = list_all_dialogue
            if page % 10 == 0:
                self.save_text()

    def get_comment_in_page(self, url):
        list_dialogue = []
        self.driver.get(url)
        javascript = "window.scrollBy(0,4000);"
        self.driver.execute_script(javascript)
        time.sleep(2)
        self.click_load_more()
        soup = self.parse_html()
        list_box_comment = soup.findAll("div", class_="jsx-691990575 thread-comment__wrapper")
        for box in list_box_comment:
            list_dialogue.append(self.get_dialogue(box))
        return list_dialogue

    def get_dialogue(self, box):
        diaglogue = []
        main_comment = box.find("div", class_="jsx-691990575 thread-comment__box")
        if main_comment is None:
            return diaglogue
        user_name = main_comment.find("a", class_="jsx-691990575 author-name")
        text = main_comment.find("span", class_="xf-body-paragraph")
        if (user_name is not None) and (text is not None):
            diaglogue.append({"user_name": user_name.text, "text": text.get_text(strip=True, separator=" ")})
            self.number_comment += 1
        list_reply = box.findAll("div", class_="jsx-3765928931 thread-comment__container")
        for reply in list_reply:
            user_name = reply.find("a", class_="jsx-3765928931 author-name")
            text_tag = reply.find("span", class_="bdPostTree_ParentPoster")
            if text_tag is not None:
                text = text_tag.text + ": "
                if text_tag.nextSibling is not None:
                    text += text_tag.nextSibling.get_text(strip=True)
            else:
                text_tag = reply.find("div", class_="jsx-1268062893 xfBody")
                if text_tag is None:
                    continue
                else:
                    text = text_tag.get_text(strip=True)
            if user_name is not None:
                diaglogue.append({"user_name": user_name.text, "text": text})
                self.number_comment += 1
        return diaglogue

    def extract_data(self):
        self.access_website()
        javascript = "window.scrollBy(0,4000);"
        self.driver.execute_script(javascript)
        time.sleep(2)
        soup = self.parse_html()
        self.number_page_comment = self.get_number_page_comment(soup)
        self.title = self.get_title(soup)
        self.content = self.get_content(soup)
        self.get_all_comment()
        self.save_text()
        self.driver.close()

    def save_text(self):
        file_data_folder = self.path_save_data + self.keyword + "/" + self.id
        path_text = self.path_save_data + self.keyword + "/"
        os.makedirs(path_text, exist_ok=True)
        json.dump(self.dict_data, open(file_data_folder + ".json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=4)

    @property
    def dict_data(self):
        return {"_id": self.id,
                "url": self.url,
                "keyword": self.keyword,
                "title": self.title,
                "content": self.content,
                "number_of_comment": self.number_comment,
                "number_of_page_comment": self.number_page_comment,
                "comment": self.comments}


