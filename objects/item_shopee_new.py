import os
import time
import re
import json

import requests
from bs4 import BeautifulSoup

from utils.utils import setup_selenium_firefox
from objects.item import Item
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class ItemShopee(Item):

    def __init__(self, url: str, keyword: str, path_save_data):
        super(ItemShopee, self).__init__(url)
        self.keyword = keyword
        self.path_save_data = path_save_data
        self.html = None
        self.main_information = None
        self.shop_information = None
        self.detail_information = None
        self.description = None
        self.comments = None
        self.image = []
        self.video = []
        self.link_video = []
        self.link_image = []

    def get_html(self):
        res = ""
        driver = setup_selenium_firefox()
        for _ in range(5):
            try:
                driver.get(self.url)
                driver.get(self.url)
                break
            except:
                res = None
                continue

        if res is None:
            self.html = None
            driver.close()
            return self.html
        javascript = "window.scrollBy(0,4000);"
        # wait = WebDriverWait(driver, 10)
        # try:
        #     wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Mzs0kz")))
        # except:
        #     pass
        time.sleep(5)
        self.html = BeautifulSoup(driver.page_source, "lxml")
        self.get_image_link()
        driver.execute_script(javascript)
        time.sleep(2)
        driver.execute_script(javascript)
        time.sleep(2)
        driver.execute_script(javascript)
        time.sleep(2)
        self.html = BeautifulSoup(driver.page_source, "lxml")
        driver.close()

    def get_main_information(self):
        main_information = {}
        # NAME
        element_name = self.html.find("div", class_="VCNVHn")
        if element_name is not None:
            element_name = element_name.find("span")
            main_information["name"] = element_name.text
        else:
            main_information["name"] = ""
        # PRICE
        original_price_tag = self.html.find("div", class_="CDN0wz")
        if original_price_tag is not None:
            original_price = original_price_tag.text
        else:
            original_price = ""

        current_price_tag = self.html.find("div", class_="pmmxKx")
        if current_price_tag is not None:
            current_price = current_price_tag.text
        else:
            current_price = ""
        discount_tag = self.html.find("div", class_="lTuS3S")
        if discount_tag is not None:
            discount = discount_tag.text
        else:
            discount = ""

        price = {"giá_gốc": original_price, "giá_hiện_tại": current_price, "giảm_giá": discount}
        main_information["price"] = price

        # COLOR/SIZE
        box_attribute = self.html.find("div", class_="PMuAq5")
        if box_attribute is None:
            self.main_information = main_information
            return
        list_attribute = box_attribute.findAll("div", class_="flex items-center")
        if not len(list_attribute):
            self.main_information = main_information
            return
        for attr in list_attribute:
            name_attr = attr.find("label", class_="_0b8hHE")
            if name_attr is None:
                continue
            name = name_attr.text.lower().replace(" ","_")
            list_variation_tag = attr.findAll("button", class_="product-variation")
            if not len(list_variation_tag):
                continue
            list_var = [attr.text for attr in list_variation_tag]
            if len(list_var):
                main_information[name] = list_var

        self.main_information = main_information
        return self.main_information

    def get_shop_information(self):
        shop_information = {}
        box_shop_information = self.html.find("div", class_="JfALJ- page-product__shop")
        if box_shop_information is None:
            self.shop_information = None
            return self.shop_information
        # NAME SHOP
        shop_name_tag = box_shop_information.find("div", class_= "_6HeM6T")
        if shop_name_tag is None:
            shop_name = None
        else:
            shop_name = shop_name_tag.text
        shop_information["tên_shop"] = shop_name
        # DETAIL SHOP
        detail_shop = {}
        box_detail = box_shop_information.find("div", class_="biYJq8")
        if box_detail is None:
            shop_information["thông_tin_chi_tiết"] = detail_shop
            self.shop_information = shop_information
            return self.shop_information

        list_element_detail = box_detail.findAll("div", class_="pHNb7U cgFEJd")
        sp_tag = box_detail.find("a", class_="Um7a0Z cgFEJd")
        if sp_tag is not None:
            list_element_detail.append(sp_tag)
        if len(list_element_detail):
            for detail in list_element_detail:
                name_tag = detail.find("label", class_="IsIIpb")
                attr_tag = detail.find("span", class_="_32ZDbL")
                if attr_tag is None:
                    attr_tag = detail.find("span", class_="_32ZDbL g54jiy")
                if attr_tag is not None and name_tag is not None:
                    detail_shop[name_tag.text] = attr_tag.text
        shop_information["thông_tin_chi_tiết"] = detail_shop
        self.shop_information = shop_information
        return self.shop_information

    # DETAIL INFORMATION
    def get_detail_information(self):
        dict_detail = {}
        box_element_detail = self.html.find("div", class_="KqLK01")
        if box_element_detail is None:
            self.detail_information = None
            return self.detail_information
        list_element_detail = box_element_detail.findAll("div", class_="_3Xk7SJ")
        if not len(list_element_detail):
            self.detail_information = None
            return self.detail_information
        for each_detail_tag in list_element_detail:
            name_tag = each_detail_tag.find("label", class_="UWd0h4")
            attr_tag = each_detail_tag.find("div")
            if name_tag is not None and attr_tag is not None:
                if len(attr_tag.findAll("a")):
                    list_attr = [attr.text for attr in attr_tag.findAll("a")]
                    text = ">".join(list_attr)
                    dict_detail[name_tag.text] = text
                else:
                    dict_detail[name_tag.text] = attr_tag.text
        self.detail_information = dict_detail
        return self.detail_information

    def get_description(self):
        element_description = self.html.find("p", class_="hrQhmh")
        if element_description is None:
            self.description = None
            return self.description
        self.description = element_description.text
        return self.description

    def get_comments(self):
        list_comments = []
        box_comments = self.html.findAll("div", class_="shopee-product-rating__main")
        if not len(box_comments):
            return self.comments
        for each in box_comments:
            each_comment = each.find("div", class_="Em3Qhp")
            each_respone = each.find("div", class_="PG51U+")
            if each_comment is None:
                continue
            if each_respone is None:
                list_comments.append({"comments": each_comment.text, "reply": ""})
            else:
                list_comments.append({"comments": each_comment.text, "reply": each_respone.text})
        self.comments = list_comments
        return self.comments

    def get_image_link(self):
        if len(self.image):
            return
        # box_images = []
        # for _ in range(5):
        box_images = self.html.findAll("div", class_="y1rHjh")
            # if len(box_images):
            #     break
        list_images = []

        if not len(box_images):
            # print(f"NONE IMAGE: {self.url} , {self.id}")
            # print(self.html.find("div", class_="agPpyA _8akja2").get("style"))
            return self.image
        for each in box_images:
            each_image = each.find("div", class_="Mzs0kz")
            if each_image is None:
                continue
            each_image = each_image.find("div", class_="agPpyA _8akja2")
            if each_image is None:
                continue
            style = each_image.get("style")
            if style != "":
                _, start = re.search(r"""[(]["]""", style).span()
                end, _ = re.search(r"""["][)]""", style).span()
                list_images.append(style[start:end])
        self.link_image = list_images
        for i in range(len(list_images)):
            dir_img = self.path_save_data + self.keyword + "/" + "image/" + self.id + "/" + str(i) + '.jpg'
            self.image.append(dir_img)
        return self.image

    def get_video_link(self):
        list_video = []
        box_video = self.html.find("div", class_="center ZCd4YG")
        if box_video is None:
            return self.video
        tag_video = box_video.find("video")
        if tag_video is None:
            return self.video
        src_video = tag_video.get("src")
        if src_video is not None:
            list_video.append(src_video)
        self.link_video = list_video
        self.video = self.path_save_data + self.keyword + "/video/" + self.id + "/" + "video.mp4"
        return self.video

    def save_text(self):
        file_data_folder = self.path_save_data + self.keyword + "/text/" + self.id
        if self.main_information is None:
            print("ERROR SHOPEEEE")
            return
        path_text = self.path_save_data + self.keyword + "/text"
        os.makedirs(path_text, exist_ok= True)
        json.dump(self.dict_data, open(file_data_folder + ".json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=4)

    def save_image(self):
        if not len(self.link_image):
            # print(self.image, self.url)
            return
        path_image = self.path_save_data + self.keyword + "/image/" + self.id
        os.makedirs(path_image, exist_ok=True)
        for i in range(len(self.link_image)):
            img = self.link_image[i]
            filename = self.path_save_data + self.keyword + "/image/" + self.id + "/" + str(i) + '.jpg'
            with open(filename, 'wb') as f:
                f.write(requests.get(img).content)

    def save_video(self):
        filename = self.path_save_data + self.keyword + "/video/" + self.id + "/" + "video.mp4"
        if not len(self.link_video):
            return
        path_video = self.path_save_data + self.keyword + "/video/" + self.id
        os.makedirs(path_video, exist_ok=True)
        src_video = self.link_video[0]
        with open(filename, 'wb') as f:
            f.write(requests.get(src_video).content)

    def extract_information(self):
        self.get_main_information()
        self.get_shop_information()
        self.get_detail_information()
        self.get_description()
        self.get_comments()
        self.get_image_link()
        self.get_video_link()

    def create_folder_save_data(self):
        path_text = self.path_save_data + self.keyword + "/text"
        os.makedirs(path_text, exist_ok= True)
        path_image = self.path_save_data + self.keyword + "/image/" + self.id
        os.makedirs(path_image, exist_ok=True)
        path_video = self.path_save_data + self.keyword + "/video/" + self.id
        os.makedirs(path_video, exist_ok=True)

    def check_login_require(self):
        login_require = self.html.find("div", class_="K1dDgL")
        # print(login_require)
        if login_require is not None:
            print("SHOPEE REQUIRE LOGIN")
            return True
        else:
            return False

    def extract_data(self):
        self.get_html()
        if self.html is None:
            print(f"LINK FAILED: {self.url}")
            return
        if self.check_login_require():
            return "VPN CHANGE"

        self.extract_information()
        if self.main_information["name"] == "":
            return
        # self.create_folder_save_data()
        # print(self.image)
        self.save_text()
        self.save_image()
        self.save_video()

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


