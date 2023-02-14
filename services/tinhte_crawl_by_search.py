import time
import re
import os

from bs4 import BeautifulSoup
from utils.utils import setup_selenium_firefox


class TinhTeCrawlBySearch:

    def __init__(self, url, path_save_data: str):
        self.origin = "https://tinhte.vn/"
        self.path_save_data = path_save_data
        self.keyword = None
        self.url = url
        self.number_page = 0
        self.page_current = 1
        self.list_item_crawled = []
        self.setup_keyword()
        self.load_list_item_crawled()

    @staticmethod
    def request_html(url):
        res = ""
        driver = setup_selenium_firefox()
        for _ in range(5):
            try:
                driver.get(url)
                res = driver.page_source
                break
            except Exception as e:
                print(f"ERROR IN REQUEST HTML: {e}")
                res = None
        driver.close()
        if res is None:
            print("CAN'T ACCESS URL")
            return None
        soup = BeautifulSoup(res, "lxml")
        return soup

    @staticmethod
    def get_total_page(soup):
        tag_number_page = soup.find("span", class_="pageNavHeader")
        if tag_number_page is None:
            return None
        text_tag_page = tag_number_page.text
        start, end = re.search("/", text_tag_page).span()
        number_total_page = int(text_tag_page[end:].strip())
        return number_total_page

    @staticmethod
    def get_keyword(soup):
        tag_keyword = soup.find("div", class_="titleBar")
        if tag_keyword is None:
            return None
        tag_keyword = tag_keyword.find("h1")
        if tag_keyword is None:
            return None
        return tag_keyword.text

    def setup_keyword(self):
        while True:
            soup = self.request_html(self.url)
            if soup is not None:
                self.number_page = self.get_total_page(soup)
                self.keyword = self.get_keyword(soup)
            else:
                t = 1
                print(f"Wait {t} minute because of error requesting HTML")
                time.sleep(t * 60)
            if (self.number_page is None) and (self.keyword is None):
                continue
            else:
                break

    def get_link_in_page(self, page):
        url = self.url + "page-" + str(page)
        soup = None
        while True:
            try:
                soup = self.request_html(url)
                if soup is not None:
                    break
                else:
                    t = 1
                    print(f"Wait {t} minute")
                    time.sleep(t*60)
            except Exception as e:
                print(f"Error get link: {e}")
                continue
        list_link = []
        box_list_item = soup.find("ol", class_="discussionListItems")
        if box_list_item is None:
            return list_link
        list_tag_item = box_list_item.findAll("li")
        if not len(list_tag_item):
            return list_link
        for each in list_tag_item:
            tag_href = each.find("h3", class_="title")
            if tag_href is None:
                continue
            href_tag = tag_href.find("a", class_="PreviewTooltip")
            if href_tag is None:
                continue
            href = href_tag.get("href")
            data_packet_new = {"url": "https://tinhte.vn/" + href}
            list_link.append(data_packet_new)
        return list_link

    def get_link_for_key(self):
        if self.page_current <= self.number_page:
            list_link = self.get_link_in_page(self.page_current)
            print(f"GET LINK IN PAGE {self.page_current}. NUMBER LINK IN PAGE {self.page_current}: {len(list_link)}")
            self.page_current += 1
            return list_link
        else:
            return "DONE"

    def load_list_item_crawled(self):
        file_data_folder = self.path_save_data + self.keyword + "/"
        if os.path.exists(file_data_folder):
            list_item = os.listdir(file_data_folder)
            list_1 = [item.replace(".json", "") for item in list_item]
        else:
            list_1 = []
        # print(f" NEW:{len(list_1)}")
        # list_2 = []
        # print(f" OLD:{len(list_2)}")
        # list_total = list_1 + list_2
        # list_total = list(set(list_total))
        # print(f" Total:{len(list_total)}")
        self.list_item_crawled = list_1
        return self.list_item_crawled

