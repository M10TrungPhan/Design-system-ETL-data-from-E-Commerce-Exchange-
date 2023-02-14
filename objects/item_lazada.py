import os
import time
import re
import json
import hashlib
import requests
from bs4 import BeautifulSoup

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from utils.utils import setup_selenium_firefox
from objects.item import Item


class ItemLazada(Item):
    def __init__(self, data_packet: dict, keyword: str, path_save_data):
        super(ItemLazada, self).__init__(data_packet)
        self.url = data_packet["url"]
        self.id = self.item_id
        self.keyword = keyword
        self.path_save_data = path_save_data
        self.driver = None
        self.list_color_img = []
        self.main_information = None
        self.shop_information = None
        self.detail_information = None
        self.description = None
        self.comments = []
        self.image = []
        self.video = []
        self.link_video = []
        self.link_image = []

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

    def parse_html(self):
        return BeautifulSoup(self.driver.page_source, "lxml")

    def get_main_information(self):
        main_information = {}
        soup = self.parse_html()
        # NAME
        element_name = soup.find("h1", class_="pdp-mod-product-badge-title")
        if element_name is not None:
            main_information["name"] = element_name.text
        else:
            main_information["name"] = ""
        # PRICE
        original_price_tag = soup.find("span", class_="pdp-price pdp-price_type_deleted "
                                                      "pdp-price_color_lightgray pdp-price_size_xs")
        if original_price_tag is not None:
            original_price = original_price_tag.text
        else:
            original_price = ""

        current_price_tag = soup.find("span", class_="pdp-price pdp-price_type_normal "
                                                     "pdp-price_color_orange pdp-price_size_xl")
        if current_price_tag is not None:
            current_price = current_price_tag.text
        else:
            current_price = ""

        discount_tag = soup.find("span", class_="pdp-product-price__discount")
        if discount_tag is not None:
            discount = discount_tag.text
        else:
            discount = ""

        price = {"giá_gốc": original_price, "giá_hiện_tại": current_price, "giảm_giá": discount}
        main_information["price"] = price

        # COLOR/SIZE
        box_attribute = self.driver.find_elements(By.CLASS_NAME, value="sku-selector")
        if not len(box_attribute):
            self.main_information = main_information
            return

        list_attribute = box_attribute[0].find_elements(By.CLASS_NAME,
                                                        value="pdp-mod-product-info-section.sku-prop-selection")
        if not len(list_attribute):
            self.main_information = main_information
            return

        for attr in list_attribute:
            name_attr = attr.find_element(By.CLASS_NAME, value="section-title")
            if name_attr is None:
                continue
            name = name_attr.text.lower().replace(" ", "_")
            list_var = []
            if len(attr.find_elements(By.CLASS_NAME, value="sku-variable-img-wrap")):
                list_color_img = self.get_list_color(attr)
                for each in list_color_img:
                    list_var.append(each[0])
                main_information[name] = list_var
                continue

            list_variation_tag = attr.find_elements(By.CLASS_NAME, value="sku-variable-name-text")
            if not len(list_variation_tag):
                continue
            list_var = [attr.text for attr in list_variation_tag]
            if len(list_var):
                main_information[name] = list_var

        self.main_information = main_information
        return self.main_information

    def get_list_color(self, attr_color):
        list_color_img = []
        list_color_tag = attr_color.find_elements(By.CLASS_NAME, value="sku-variable-img-wrap")
        list_color_tag.append(attr_color.find_element(By.CLASS_NAME, value="sku-variable-img-wrap-selected"))
        for each_tag in list_color_tag:
            each_tag.click()
            src_img = self.driver.find_element(By.CLASS_NAME, value="pdp-mod-common-image.gallery-preview"
                                                                    "-panel__image").get_attribute("src")
            color = self.driver.find_element(By.CLASS_NAME, value="sku-name").text.lower()
            list_color_img.append((color, src_img))
        self.list_color_img = list_color_img
        return list_color_img

    # SHOP INFORMATION
    def get_shop_information(self):
        shop_information = {}
        soup = self.parse_html()
        box_shop_information = soup.find("div", class_="seller-container")
        if box_shop_information is None:
            self.shop_information = None
            return self.shop_information
        # NAME SHOP
        shop_name_tag = box_shop_information.find("div", class_="seller-name__detail").find("a")
        if shop_name_tag is None:
            shop_name = None
        else:
            shop_name = shop_name_tag.text
            if not len(shop_name):
                shop_name = shop_name_tag["alt"]
        shop_information["tên_shop"] = shop_name
        # DETAIL SHOP
        detail_shop = {}
        list_tag_detail = soup.findAll("div", class_="info-content")
        if not len(list_tag_detail):
            shop_information["thông_tin_chi_tiết"] = detail_shop
            self.shop_information = shop_information
            return self.shop_information
        for each_tag in list_tag_detail:
            key_tag = each_tag.find("div", class_="seller-info-title")
            if key_tag is None:
                continue
            value_tag = key_tag.find_next_sibling()
            if value_tag is None:
                continue
            key = key_tag.text.lower().strip().replace(" ", "_")
            value = value_tag.text
            detail_shop[key] = value
        shop_information["thông_tin_chi_tiết"] = detail_shop
        self.shop_information = shop_information
        return self.shop_information

    # DETAIL INFORMATION
    def get_detail_information(self):
        dict_detail = {}
        soup = self.parse_html()
        list_tag_detail = soup.findAll("li", class_="key-li")
        # print(len(list_tag_detail))
        for each_tag in list_tag_detail:
            key_detail = each_tag.find("span", class_="key-title")
            value_detail = each_tag.find("div", class_="key-value")
            if key_detail is not None and value_detail is not None:
                key_detail = key_detail.text.lower().strip().replace(" ", "_")
                dict_detail[key_detail] = value_detail.text

        self.detail_information = dict_detail
        return self.detail_information

    def get_description(self):
        button = self.driver.find_elements(By.CLASS_NAME,
                                           value="pdp-view-more-btn.pdp-button.pdp-button_type_text.pdp-button_theme_white.pdp-button_size_m")
        if len(button):
            button[0].click()
        soup = self.parse_html()
        box_description = soup.find("div", class_="html-content pdp-product-highlights")
        if box_description is None:
            box_description = soup.find("div", class_="html-content detail-content")
        if box_description is None:
            self.description = None
            return self.description
        self.description = box_description.get_text(strip=True, separator=" ")
        return self.description

    # COMMENT
    def get_comments(self):
        list_comments = []
        soup = self.parse_html()
        box_comments = soup.findAll("div", class_="item")
        if not len(box_comments):
            return self.comments
        for each in box_comments:
            each_comment = each.find("div", class_="item-content")
            if each_comment is None:
                continue
            each_comment = each_comment.find("div", class_="content")
            if each_comment is None:
                continue
            each_respone = each.find("div", class_="seller-reply-wrapper")
            if each_respone is None:
                list_comments.append({"comments": each_comment.text, "reply": ""})
            else:
                comment = each_respone.find("div", class_="content")
                if comment is None:
                    comment = ""
                else:
                    comment = comment.text
                list_comments.append({"comments": each_comment.text, "reply": comment})
        self.comments = list_comments
        return self.comments

    #
    def get_image_link(self):
        if len(self.list_color_img):
            list_image_1 = [each[1] for each in self.list_color_img]
        else:
            list_image_1 = []
        soup = self.parse_html()
        list_image_2 = soup.findAll("img", class_="pdp-mod-common-image item-gallery__thumbnail-image")
        list_image_2 = [tag.get("src").replace("120x120", "720x720").replace("80x80", "720x720") for tag in list_image_2]
        list_diff = list(set(set(list_image_1) ^ set(list_image_2)))
        list_diff = [each for each in list_diff if each not in list_image_1]
        for i in range(len(list_diff)):
            name = "Unknown" + str(i)
            self.list_color_img.append((name, list_diff[i]))
        return self.list_color_img

    def save_text(self):
        file_data_folder = self.path_save_data + self.keyword + "/text/" + self.id
        if self.main_information is None:
            print("ERROR SHOPEEEE")
            return
        path_text = self.path_save_data + self.keyword + "/text"
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
            name = element[0].replace(" ", "_").lower()
            filename = self.path_save_data + self.keyword + "/image/" + self.id + "/" + name + '.jpg'
            with open(filename, 'wb') as f:
                f.write(requests.get(img).content)
            if os.path.exists(filename):
                self.image.append(filename)
        return self.image

    def get_video_link(self):
        list_video = []
        try:
            self.driver.find_element(By.CLASS_NAME, value="gallery-preview-panel__content.gallery-preview-panel__content_video").click()
        except:
            return
        time.sleep(5)
        soup = self.parse_html()
        list_video.append(soup.find("video").get("src"))
        self.driver.find_element(By.CLASS_NAME, value="next-dialog-close").click()
        self.link_video = list_video
        return self.link_video

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
        self.get_video_link()
        self.get_main_information()
        if self.main_information["name"] == "":
            self.driver.close()
            return
        self.get_image_link()
        self.get_shop_information()
        javascript = "window.scrollBy(0,1000);"
        self.driver.execute_script(javascript)
        time.sleep(3)
        self.get_description()
        javascript = "window.scrollBy(0,1000);"
        self.driver.execute_script(javascript)
        time.sleep(2)
        javascript = "window.scrollBy(0,1000);"
        self.driver.execute_script(javascript)
        time.sleep(2)
        self.get_detail_information()
        self.get_comments()
        self.save_image()
        self.save_video()
        self.save_text()
        self.driver.close()
    # def check_login_require(self):
    #     login_require = self.html.find("div", class_="K1dDgL")
    #     # print(login_require)
    #     if login_require is not None:
    #         print("SHOPEE REQUIRE LOGIN")
    #         return True
    #     else:
    #         return False

    def extract_data(self):
        if self.access_website() is None:
            print(f"LINK FAILED: {self.url}")
            return
        self.extract_information()

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
