import concurrent.futures
import os
import threading
import time
from queue import Queue
from threading import Thread
import logging
from utils.utils import change_vpn, import_from_string
from config.config import Config


class Crawler(Thread):

    def __init__(self, search_key_service, item_class, number_crawler: int):
        super(Crawler, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.number_crawler = number_crawler
        self.item_class_web = item_class
        self.search_key_service = search_key_service
        self.path_save_data = self.search_key_service.path_save_data
        self.flag_finish = False
        self.flag_vpn = 0
        self.queue_item = Queue()
        self.chang_ip_time = 0
        self.queue_manage_crawler = Queue()
        self.number_item_crawl_successful = 0

    # GET ITEM IN QUEUES AND CRAWL
    def crawl(self):
        if not self.queue_item.qsize():
            self.queue_manage_crawler.get()
            return
        url = self.queue_item.get()
        item = self.item_class_web(url, self.search_key_service.keyword, self.path_save_data)
        status = ""
        if item.id in self.search_key_service.list_item_crawled:
            self.queue_manage_crawler.get()
            return
        try:
            # print(f"START CRAWL {item.id}")
            status = item.extract_data()
        except Exception as error:
            self.logger.error(f"ERROR IN {item.url}: {error}")
        try:
            item.driver.close()
        except:
            pass
        # CHECK WEBSITE BAN IP (FOR SHOPEE)
        if status == "VPN CHANGE":
            self.rotate_vpn()
            change_vpn()
            self.queue_manage_crawler.get()
            return
        self.search_key_service.list_item_crawled.append(item.id)
        self.number_item_crawl_successful += 1
        self.queue_manage_crawler.get()

    # CHANGE VPN IF WEBSITE BAN IP
    def rotate_vpn(self):
        if self.flag_vpn:
            return
        self.flag_vpn = 1
        change_vpn()
        self.flag_vpn = 0

    # def change_vpn(self):
    #     time.sleep(10)
    #     list_country = ["Viet nam", "Italy", "United States", "Spain", "Japan", "Taiwan", "Hong Kong"]
    #     country = random.choice(list_country)
    #     os.system("""nordvpn.lnk -c -g "{}" """.format(country))
    #     print(f"CONNECT VPN IN {country}")
    #     time.sleep(15)

    # GET LINK AND PUT TO QUEUE
    def manage_crawler(self):
        while True:
            if self.queue_item.qsize() < 2 * self.number_crawler:
                list_link = self.search_key_service.get_link_for_key()
                if list_link == "DONE":
                    self.flag_finish = True
                    break
                else:
                    for each in list_link:
                        self.queue_item.put(each)
            time.sleep(15)

    def thread_crawler(self):
        while True:
            if (not self.queue_item.qsize()) and (self.flag_finish == True):
                return
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.number_crawler) as executor:
                [executor.submit(self.crawl) for _ in range(self.number_crawler)]
            self.chang_ip_time += 1
            if self.chang_ip_time % 100 == 0:
                print("CHANGE VPN ")
                # self.rotate_vpn()
            time.sleep(5)

    # CREATE FOLDER TO SAVE DATA
    def create_folder_save_data(self):
        os.makedirs(self.path_save_data, exist_ok=True)

    def thread_manage_number_crawler(self):
        flag_notification = 0
        while self.queue_item.qsize() or not self.flag_finish:
            flag_notification += 1
            if self.queue_manage_crawler.qsize() < self.number_crawler:
                for _ in range(self.number_crawler):
                    if self.queue_manage_crawler.qsize() < self.number_crawler:
                        thread_request_next_page = threading.Thread(target=self.crawl)
                        thread_request_next_page.start()
                        self.queue_manage_crawler.put(1)
            if not(flag_notification % 30):
                self.logger.info(f"NUMBER ITEM CRAWLED SUCCESSFUL: {self.number_item_crawl_successful}")
            time.sleep(10)

        print("DONE THREAD CRAWLER")

    def run(self):
        self.logger.info(f"SERVICE GET KEY {self.search_key_service.__class__.__name__}")
        self.logger.info(f"ITEM CRAWL {self.item_class_web.class_name()}")
        self.create_folder_save_data()
        manage_crawler = threading.Thread(target=self.manage_crawler)
        manage_crawler.start()
        crawler = threading.Thread(target=self.thread_manage_number_crawler)
        crawler.start()
        crawler.join()
        manage_crawler.join()
        self.logger.info(f"FINISH CRAWL {self.number_item_crawl_successful} {self.item_class_web.class_name()} "
                         f"WITH KEYWORD {self.search_key_service.keyword}")


if __name__ == "__main__":

    ########################################################
    # SHOPEE
    from objects.item_shopee_ver2 import ItemShopee
    from services.shopee_crawl_by_search_new import ShopeeCrawlBySearch
    print("Shopee")
    path = "D:/Shoppe_data/"
    # path_folder_data = "D:/Shoppe_data/"
    # list_key_id = os.listdir(path_folder_data)
    # list_key = [key.replace("_id.json", "") for key in list_key_id]
    list_key = [ "Sách"]
    print(list_key)

    for key in list_key:
        print(f"Crawler: {key} ")
        search = ShopeeCrawlBySearch(key, path)
        search.number_page = 30
        crawl_vbpl = Crawler(search, ItemShopee, 5)
        crawl_vbpl.start()
        crawl_vbpl.join()
        print(f"DONE {key}")
    time.sleep(60*10)

    ####################################################################
    # TIKI
    from objects.item_tiki import ItemTiki
    from services.tiki_crawl_by_search import TikiCrawlBySearch
    print("Tiki")
    path = "D:/Tiki_data/"
    # path_folder_data = "D:/Shoppe_data/"
    # list_key_id = os.listdir(path_folder_data)
    # list_key = [key.replace("_id.json", "") for key in list_key_id]
    list_key = ["Bàn", "Ghế", "Quạt", "Sách", "Xe máy", "Ô tô"]
    for key in list_key:
        print(f"Crawler: {key} ")
        search = TikiCrawlBySearch(key, path)
        search.number_page = 21
        crawl = Crawler(search, ItemTiki, 5)
        crawl.start()
        crawl.join()
        print(f"DONE {key}")
    time.sleep(60*10)
    ###################################################################
    # LAZADA
    from  services.lazada_crawl_by_search import LazadaCrawlBySearch
    from objects.item_lazada import ItemLazada
    print("LAZADA")
    path = "D:/testst/"
    key = "Áo thun"
    search = LazadaCrawlBySearch(key, path)
    crawl_lazada = Crawler(search, ItemLazada, 2)
    crawl_lazada.start()

    ###################################################################
    # TINH TE
    from services.tinhte_crawl_by_search import TinhTeCrawlBySearch
    from objects.item_tinhte import ItemTinhTe
    print("TINH TE")
    path = "D:/testst/"
    list_key = [("https://tinhte.vn/forums/may-tinh-xach-tay-laptop.755/", 1),
                ("https://tinhte.vn/forums/linh-kien-thiet-bi-khac.756/", 1),
                ("https://tinhte.vn/forums/ban-phim-co.757/", 1),
                ("https://tinhte.vn/forums/may-tinh-mac-macos.748/", 1),
                ("https://tinhte.vn/forums/may-tinh-linux.79/", 1),
                ("https://tinhte.vn/forums/may-tinh-chrome-os.402/", 1),
                ("https://tinhte.vn/forums/tu-van-chon-mua-may-tinh.199/", 1),
                ("https://tinhte.vn/forums/anh-nen-wallpaper.64/", 1),
                ("https://tinhte.vn/forums/thiet-bi-mang.759/", 1)]
    # key = "https://tinhte.vn/forums/thuong-mai-dien-tu.636/"
    for key in list_key:
        try:
            search = TinhTeCrawlBySearch(key[0], path)
            search.page_current = key[1]
            logging.info(f"CRAWLER {search.keyword}")
            crawl_tinhte = Crawler(search, ItemTinhTe, 15)
            crawl_tinhte.start()
            crawl_tinhte.join()
            logging.info(f"{search.keyword}: {search.page_current}")
            logging.info(f"DONE {search.keyword}")
        except Exception as e:
            logging.info(f"Error CrawlData pipeline: {e}")
    ######################################################################
    # TGDD
    from services.tgdd_crawl_by_search import TGDDCrawlBySearch
    from objects.item_tgdd import ItemTGDD
    print("TGDĐ")
    path = "D:/testst/"
    keyword = "Tivi"
    search = TGDDCrawlBySearch(keyword, path)
    crawl_tgdd = Crawler(search, ItemTGDD, 2)
    crawl_tgdd.start()



