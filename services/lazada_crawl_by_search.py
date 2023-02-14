import logging
import time
import json
import os

from bs4 import BeautifulSoup

from utils.utils import setup_selenium_firefox, change_vpn


class LazadaCrawlBySearch:

    def __init__(self, keyword, path_save_data):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.path_save_data = path_save_data
        self.origin = "lazada.vn"
        self.list_item_crawled = []
        self.keyword = keyword.strip()
        self.list_link = []
        self.total_link = 0
        self.number_page = 0
        self.page_current = 1
        self.number_link_in_page = 0
        # self.load_list_item_crawled()
        self.get_total_page()

    def get_keyword_encoded(self):
        return "%20".join(key for key in self.keyword.split())

    @staticmethod
    def request_html(url):
        driver = setup_selenium_firefox()
        res = ""
        for _ in range(5):
            try:
                driver.get(url)
                time.sleep(2)
                break
            except Exception as e:
                print(e)
                continue
        if res is None:
            driver.close()
            return None
        soup = BeautifulSoup(driver.page_source, "lxml")
        driver.close()
        return soup

    def get_number_total_link(self):
        while True:
            url = "https://www.{}/catalog/?_keyori=ss&ajax=" \
                  "true&from=input&isFirstRequest=true&page={}&q={}"\
                .format(self.origin, 1, self.get_keyword_encoded())
            soup = self.request_html(url)
            try:
                text = soup.find("pre").text
                text_json = json.loads(text)
                total_result = text_json["mainInfo"]["totalResults"]
                pageSize = text_json["mainInfo"]["pageSize"]
                break
            except Exception as e:
                print(e)
                self.logger.info("LAZADA BAN API GET KEYWORDS. PLEASE WAIT MINUTES")
                change_vpn()
        self.number_link_in_page = int(pageSize)
        self.total_link = int(total_result)

    def get_total_page(self):
        self.get_number_total_link()
        self.number_page = self.total_link // self.number_link_in_page
        return self.number_page

    def get_link_in_page(self, page):
        url = "https://www.{}/catalog/?_keyori=ss&ajax=true" \
              "&from=input&isFirstRequest=true&page={}&q={}".\
            format(self.origin, page, self.get_keyword_encoded())
        list_link = []

        while True:
            soup = self.request_html(url)
            if soup is None:
                return list_link
            try:
                text = soup.find("pre").text
                text_json = json.loads(text)
                break
            except:
                change_vpn()
                continue
        try:
            for d in range(self.number_link_in_page):
                link_new = "https:" + text_json["mods"]["listItems"][d]["itemUrl"]
                data_packet_new = {"url": link_new}
                list_link.append(data_packet_new)
        except KeyError:
            pass
        return list_link

    def get_link_for_key(self):
        if self.page_current <= self.number_page:
            print(f"GET LINK IN PAGE {self.page_current}")
            list_link = self.get_link_in_page(self.page_current)
            self.page_current += 1
            return list_link
        else:
            return "DONE"

    def load_list_item_crawled(self):
        file_data_folder = self.path_save_data + self.keyword + "/text/"
        if os.path.exists(file_data_folder):
            list_item = os.listdir(file_data_folder)
            list_1 = [item.replace(".json", "") for item in list_item]
        else:
            list_1 = []
        print(f" NEW:{len(list_1)}")
        list_2 = self.load_list_id()
        print(f" OLD:{len(list_2)}")
        list_total = list_1 + list_2
        list_total = list(set(list_total))
        print(f" Total:{len(list_total)}")
        self.list_item_crawled = list_total
        return self.list_item_crawled

    def load_list_id(self):
        list_id = []
        name = self.keyword + "_id" + ".json"
        file_data_folder = self.path_save_data + "Total_data_id/"
        if name not in os.listdir(file_data_folder):
            return list_id
        list_id = json.load(open(file_data_folder+name, 'r', encoding="utf-8"))
        return list_id