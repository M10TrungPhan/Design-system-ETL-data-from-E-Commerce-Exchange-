import os
import time
import re
import json
import hashlib

import requests
from bs4 import BeautifulSoup

from utils.utils import setup_selenium_firefox
from selenium.webdriver.common.by import By
from objects.item import Item


class ItemTiki(Item):

    def __init__(self, data_packet: dict, keyword: str, path_save_data):
        super(ItemTiki, self).__init__(data_packet)
        self.url = data_packet["url"]
        self.id = self.item_id
        self.keyword = keyword
        self.path_save_data = path_save_data
        self.driver = None
        self.main_information = None
        self.shop_information = None
        self.detail_information = None
        self.description = None
        self.comments = None
        self.image = []
        self.video = []
        self.link_video = []
        self.list_color_img = []

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
        time.sleep(5)
        return self.parse_html()

    def parse_html(self):
        return BeautifulSoup(self.driver.page_source, "lxml")

    def get_main_information(self):
        main_information = {}
        soup = self.parse_html()
        # NAME
        element_name = soup.find("div", class_="header")
        if element_name is not None:
            element_name = element_name.find("h1", class_="title")
            main_information["name"] = element_name.text
        else:
            main_information["name"] = ""
        self.main_information = main_information

        return self.main_information

    @staticmethod
    def parse_link_image(style):
        if style != "":
            _, start = re.search(r"""[(]["]""", style).span()
            end, _ = re.search(r"""["][)]""", style).span()
            return style[start:end]
        return None

    def get_shop_information(self):
        return self.shop_information

    # DETAIL INFORMATION
    def get_detail_information(self):
        return self.detail_information

    def get_description(self):
        return self.description

    def get_comments(self):
        return self.comments

    def get_image_link(self):
        if len(self.list_color_img):
            list_image_1 = [each[1] for each in self.list_color_img]
        else:
            list_image_1 = []
        try:
            view_image_more = self.driver.find_element(By.CLASS_NAME, value="open-gallery")
            view_image_more.click()
            time.sleep(2)
        except:
            return self.list_color_img
        soup = self.parse_html()
        list_image_2 = []
        box_images = soup.findAll("img", class_="style__SmallImage-sc-l7yr9-3 fHidWR")
        for each_box in box_images:
            src_img = each_box.get("src")
            # src_img = self.parse_link_image(src_img).replace("_tn", "")
            list_image_2.append(src_img)
        list_diff = list(set(set(list_image_1) ^ set(list_image_2)))
        list_diff = [each for each in list_diff if each not in list_image_1]
        for i in range(len(list_diff)):
            name = "Unknown" + str(i)
            self.list_color_img.append((name, list_diff[i]))
        return self.list_color_img

    def get_video_link(self):
        return self.link_video

    def save_text(self):
        file_data_folder = self.path_save_data + self.keyword + "/text/" + self.id
        path_text = self.path_save_data + self.keyword + "/text/"
        os.makedirs(path_text, exist_ok=True)
        json.dump(self.dict_data, open(file_data_folder + ".json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=4)

    def save_image(self):
        if not len(self.list_color_img):
            return
        path_image = self.path_save_data + self.keyword + "/image/" + self.id
        os.makedirs(path_image, exist_ok=True)
        for element in self.list_color_img:
            img = element[1]
            name = element[0].replace(" ", "_").replace(r"\\", "_").lower()
            name = re.sub(r"""[?/*"<>=|]""", "_", name)
            filename = self.path_save_data + self.keyword + "/image/" + self.id + "/" + name + '.jpg'
            for _ in range(5):
                try:
                    with open(filename, 'wb') as f:
                        f.write(requests.get(img).content)
                    break
                except:
                    pass
            if os.path.exists(filename):
                self.image.append(filename)
        return self.image

    def save_video(self):
        filename = self.path_save_data + self.keyword + "/video/" + self.id + "/" + "video.mp4"
        if not len(self.link_video):
            return
        path_video = self.path_save_data + self.keyword + "/video/" + self.id
        os.makedirs(path_video, exist_ok=True)
        src_video = self.link_video[0]
        with open(filename, 'wb') as f:
            f.write(requests.get(src_video).content)
        if os.path.exists(filename):
            self.video.append(filename)

    def extract_information(self):
        # self.get_video_link()
        self.get_main_information()
        self.get_image_link()
        # print(self.list_color_img, self.image)
        # javascript = "window.scrollBy(0,4000);"
        # self.driver.execute_script(javascript)
        # time.sleep(2)
        # self.driver.execute_script(javascript)
        # time.sleep(2)
        # self.driver.execute_script(javascript)
        # time.sleep(2)
        # self.get_shop_information()
        # self.get_detail_information()
        # self.get_description()
        # self.get_comments()
        # print(self.dict_data)
        self.driver.close()

    def check_login_require(self):
        soup = self.parse_html()
        login_require = soup.find("div", class_="K1dDgL")
        if login_require is not None:
            print("SHOPEE REQUIRE LOGIN")
            return True
        else:
            return False

    def check_available_web(self):
        soup = self.parse_html()
        available = soup.find("button", class_="ELFjnM")
        if available is not None:
            print("SHOPEE NOT AVAILABLE")
            return True
        else:
            return False

    def extract_data(self):
        if self.access_website() is None:
            print(f"LINK FAILED: {self.url}")
            self.driver.close()
            return
        # if self.check_login_require():
        #     self.driver.close()
        #     return "VPN CHANGE"
        # if self.check_available_web():
        #     self.driver.close()
        #     return "VPN CHANGE"
        self.extract_information()
        if self.main_information["name"] == "":
            # self.driver.close()
            return
        if not len(self.list_color_img):
            return
        print(self.main_information)
        self.save_text()
        self.save_image()
        # self.save_video()

    @property
    def dict_data(self):
        return {"_id": self.id,
                "url": self.url,
                "keyword": self.keyword,
                "main_information": self.main_information,
                "shop_information": self.shop_information,
                "detail": self.detail_information,
                "description": self.description,
                "comments": self.comments,
                "image": self.image,
                "video": self.video}


