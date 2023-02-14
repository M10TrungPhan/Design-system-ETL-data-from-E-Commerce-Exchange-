import os.path
import time

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from utils.utils import setup_selenium_firefox


class TGDDCrawlBySearch:

    def __init__(self, keyword, path_save_data: str):
        self.origin = "https://www.thegioididong.com"
        self.path_save_data = path_save_data
        self.keyword = keyword.strip()
        self.list_link_before = []
        self.list_link_current = []
        self.driver = None
        self.list_item_crawled = []
        self.access_website()
        self.load_list_item_crawled()

    def search_key(self):
        self.driver.find_element(By.CLASS_NAME, "input-search").send_keys(self.keyword)
        self.driver.find_element(By.CLASS_NAME, "icon-search").click()
        time.sleep(5)

    def access_website(self):
        self.driver = setup_selenium_firefox()
        self.driver.get(self.origin)
        time.sleep(3)
        self.search_key()
        javascript = "window.scrollBy(0,6000);"
        self.driver.execute_script(javascript)
        # self.click_view_more()
        # self.list_link_current = self.get_link_in_page(self.parse_html(self.driver.page_source))

    def click_view_more(self):
        try:
            self.driver.find_element(By.CLASS_NAME, "view-more").click()
            time.sleep(3)
            javascript = "window.scrollBy(0,1300);"
            self.driver.execute_script(javascript)
            time.sleep(10)
            return True
        except:
            pass
        try:
            self.driver.find_element(By.CLASS_NAME, "viewmore").click()
            time.sleep(3)
            javascript = "window.scrollBy(0,1300);"
            self.driver.execute_script(javascript)
            time.sleep(10)
            return True
        except:
            return False

    @staticmethod
    def get_link_in_page(soup):
        list_link = []
        box_list = soup.find("ul", class_="listsearch item2020 listproduct")
        if box_list is None:
            box_list = soup.find("ul", class_="listproduct")

        tag_a = box_list.findAll("a")
        for a in tag_a:
            link = a.get("href")
            if link is not None and link != "#":
                link_new = "https://www.thegioididong.com" + link
                data_packet_new = {"url": link_new}
                list_link.append(data_packet_new)

        # list_link = list(set(list_link))
        return list_link

    @staticmethod
    def parse_html(source):
        return BeautifulSoup(source, "lxml")

    def get_link_for_key(self):
        # javascript = "window.scrollBy(0,1000);"
        # self.driver.execute_script(javascript)
        if self.driver is None:
            return False
        if not len(self.list_link_current):
            self.list_link_current = self.get_link_in_page(self.parse_html(self.driver.page_source))
            # print(self.list_link_current[-1], "\n", len(self.list_link_current))
            return self.list_link_current
        if not self.click_view_more():
            print("Het san pham. K the click more")
            self.driver.close()
            self.driver = None
            return "DONE"
        self.list_link_before = self.list_link_current
        self.list_link_current = self.get_link_in_page(self.parse_html(self.driver.page_source))
        list_link = list(set(self.list_link_current) ^ set(self.list_link_before))
        # if not len(list_link):
        #     print("Het san pham")
        #     return False
        # print(len(list_link))
        return list_link

    def load_list_item_crawled(self):
        file_data_folder = self.path_save_data + self.keyword + "/text/"
        if os.path.exists(file_data_folder):
            list_item = os.listdir(file_data_folder)
            self.list_item_crawled = [item.replace(".json", "") for item in list_item]
        else:
            self.list_item_crawled = []
        return self.list_item_crawled
