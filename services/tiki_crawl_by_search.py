import logging
import time
import json
import os

from bs4 import BeautifulSoup
from utils.utils import setup_selenium_firefox


class TikiCrawlBySearch:

    def __init__(self, keyword, path_save_data):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.path_save_data = path_save_data
        self.list_item_crawled = []
        self.keyword = keyword
        self.total_link = 0
        self.number_page = 50
        self.page_current = 1
        self.number_link_in_page = 40
        self.load_list_item_crawled()

    def get_keyword_encoded(self):
        return "+".join(key for key in self.keyword.split())

    @staticmethod
    def request_html(url):
        driver = setup_selenium_firefox()
        res = ""
        for _ in range(5):
            try:
                driver.get(url)
                break
            except Exception as e:
                print(e)
                res = None
                continue
        if res is None:
            driver.close()
            return None
        for _ in range(5):
            javascript = "window.scrollBy(0,1000);"
            driver.execute_script(javascript)
            time.sleep(1)
        soup = BeautifulSoup(driver.page_source, "lxml")
        driver.close()
        return soup

    # def get_number_total_link(self):
    #     while True:
    #         url = "https://{}/api/v4/search/search_items?by=relevancy&keyword={}&limit={}&newest=0&order" \
    #               "=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2"\
    #             .format(self.origin, self.get_keyword_encoded(), self.number_link_in_page)
    #         print(url)
    #         soup = self.request_html(url)
    #         text = soup.find("pre").text
    #         text_json = json.loads(text)
    #         try:
    #             total_count = text_json["total_count"]
    #             break
    #         except KeyError:
    #             self.logger.info("SHOPEE BAN API GET KEYWORDS. PLEASE WAIT MINUTES")
    #             change_vpn()
    #             # time.sleep(5*30)
    #     self.total_link = total_count
    #     return self.total_link

    # def get_total_page(self):
    #     # self.get_number_total_link()
    #     self.number_page = 20
    #     print(f"Number page is {self.number_page}")
    #     return self.number_page

    # def get_link_in_page(self, page):
    #     newwest = page * self.number_link_in_page
    #     url = "https://{}/api/v4/search/search_items?by=relevancy&keyword={}&limit=100&newest={}" \
    #           "&order=desc&page_type=search&scenario=PAGE_GLOBAL_SEARCH&version=2".\
    #         format(self.origin, self.get_keyword_encoded(), newwest)
    #     soup = self.request_html(url)
    #     list_data = []
    #     list_link = []
    #     if soup is None:
    #         return list_link
    #     text = soup.find("pre").text
    #     text_json = json.loads(text)
    #     try:
    #         for d in text_json["items"]:
    #             list_data.append(d["item_basic"])
    #     except KeyError:
    #         pass
    #     for each in list_data:
    #         list_link.append(r'https://{}/{}-i.{}.{}'.format("shopee.vn", each['name'],each['shopid'], each['itemid']))
    #
    #     return list_link

    def get_link_in_page(self, page):
        url = f"https://tiki.vn/search?q={self.get_keyword_encoded()}&page={page}"

        soup = self.request_html(url)
        list_link = []
        if soup is None:
            return list_link
        box_list_item = soup.find("div", class_="ProductList__Wrapper-sc-1dl80l2-0 iPafhE")
        if box_list_item is None:
            return list_link
        list_item_element = box_list_item.findChildren("a", class_="product-item", recursive=False)
        for each in list_item_element:
            link_new = "https://tiki.vn" + each.get("href")
            data_packet_new = {"url": link_new}
            list_link.append(data_packet_new)
            # print(link_new)
            # list_link.append(link_new)
        return list_link

    def get_link_for_key(self):
        if len(self.list_item_crawled) > 500:
            return "DONE"
        if self.page_current <= self.number_page:
            list_link = self.get_link_in_page(self.page_current)
            print(f"GET LINK IN PAGE {self.page_current}")
            print(f"Number link of page {self.page_current}: {len(list_link)}")
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
        list_2 = []
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



