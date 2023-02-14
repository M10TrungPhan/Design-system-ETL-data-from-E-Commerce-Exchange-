import hashlib
import os
import time
import re
import json

import requests
from bs4 import BeautifulSoup

from utils.utils import setup_selenium_firefox
from objects.item import Item
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ItemShopee(Item):

    def __init__(self, data_package_item: dict, keyword: str, path_save_data):
        super(ItemShopee, self).__init__(data_package_item)
        self.url = data_package_item["url"]
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
        element_name = soup.find("div", class_="_2rQP1z")
        if element_name is None:
            element_name = soup.find("div", class_="YPqix5")
        if element_name is not None:
            element_name = element_name.find("span")
            main_information["name"] = element_name.text
        else:
            main_information["name"] = ""
        # PRICE
        original_price_tag = soup.find("div", class_="Kg2R-S")
        if original_price_tag is not None:
            original_price = original_price_tag.text
        else:
            original_price = ""

        current_price_tag = soup.find("div", class_="X0xUb5")
        if current_price_tag is not None:
            current_price = current_price_tag.text
        else:
            current_price = ""
        discount_tag = soup.find("div", class_="+1IO+x")
        if discount_tag is not None:
            discount = discount_tag.text
        else:
            discount = ""

        price = {"giá_gốc": original_price, "giá_hiện_tại": current_price, "giảm_giá": discount}
        main_information["price"] = price

        # COLOR/SIZE
        time.sleep(2)
        box_attribute = self.driver.find_elements(By.CLASS_NAME, value="flex tprdAj _5BeP91".replace(" ", "."))

        if not len(box_attribute):
            self.main_information = main_information
            return
        list_attribute_tag = box_attribute[0].find_elements(By.CLASS_NAME, value="flex items-center".replace(" ", "."))

        if not len(list_attribute_tag):
            self.main_information = main_information
            return

        for attr_tag in list_attribute_tag:
            if not len(attr_tag.find_elements(By.CLASS_NAME, value="flex items-center HiGScj".replace(" ", "."))):
                continue
            try:
                name_attr = attr_tag.find_element(By.TAG_NAME, value="label")
            except NoSuchElementException:
                continue
            name = name_attr.text.lower().replace(" ", "_")
            if re.search("màu|màu_sắc|màu sắc|mẫu", name, flags=re.IGNORECASE) is not None:
            # if name in ["màu", "màu_sắc", "mẫu"]:
                list_var = self.get_list_color(attr_tag)
                main_information[name] = list_var
                continue
            if name_attr is None:
                continue
            list_variation_tag = attr_tag.find_elements(By.TAG_NAME, value="button")
            if not len(list_variation_tag):
                continue
            list_var = [attr.get_attribute("aria-label") for attr in list_variation_tag]
            if len(list_var):
                main_information[name] = list_var

        self.main_information = main_information
        return self.main_information

    def get_list_color(self, attr_color):
        list_color_img = []
        list_img = []
        list_color = []
        list_color_tag = attr_color.find_elements(By.TAG_NAME, value="button")
        # print("XXXXXXXXXXXXXXXXXXXXXXXXXXXX")

        for each_tag in list_color_tag:
            each_tag.click()
            # wait = WebDriverWait(self.driver, 10)
            # element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#main > div > div:nth-child(3) > div._8ysWpr > div > div > div.container > div.product-briefing.flex.card.HZ\+iZJ > div.FYkmHR > div.flex.flex-column > div.cqcwiO > div > div.JCfBJx > div")))
            time.sleep(3)
            # self.driver.implicitly_wait(5)
            color = each_tag.get_attribute("aria-label")
            list_color.append(color)
            try:
                box_image = self.driver.find_element(By.CLASS_NAME, value="JCfBJx".replace(" ", "."))
                src_img = box_image.find_element(By.TAG_NAME, "div").get_attribute("style")
                # src_img = self.driver.find_element(By.CLASS_NAME, value="_3VFGEz wdZ+2f".replace(" ", "."))
                # src_img = src_img.get_attribute("style")
                # print(src_img)
            except:
                continue
            src_img = self.parse_link_image(src_img)
            if src_img in list_img:
                continue
            list_img.append(src_img)
            list_color_img.append((color, src_img))

        self.list_color_img = list_color_img
        return list_color

    @staticmethod
    def parse_link_image(style):
        if style != "":
            _, start = re.search(r"""[(]["]""", style).span()
            end, _ = re.search(r"""["][)]""", style).span()
            return style[start:end]
        return None

    def get_shop_information(self):
        shop_information = {}
        soup = self.parse_html()
        box_shop_information = soup.find("div", class_="_3YmilF page-product__shop")
        if box_shop_information is None:
            self.shop_information = None
            return self.shop_information
        # NAME SHOP
        shop_name_tag = box_shop_information.find("div", class_="FbKovn")
        if shop_name_tag is None:
            shop_name = None
        else:
            shop_name = shop_name_tag.text
        shop_information["tên_shop"] = shop_name
        # DETAIL SHOP
        detail_shop = {}
        box_detail = box_shop_information.find("div", class_="s1qcwz")
        if box_detail is None:
            shop_information["thông_tin_chi_tiết"] = detail_shop
            self.shop_information = shop_information
            return self.shop_information

        list_element_detail = box_detail.findAll("div", class_="ZM0I40 TgiIDB")
        sp_tag = box_detail.find("a", class_="FN6HJb TgiIDB")
        if sp_tag is not None:
            list_element_detail.append(sp_tag)
        if len(list_element_detail):
            for detail in list_element_detail:
                name_tag = detail.find("label", class_="_7wqb+H")
                attr_tag = detail.find("span", class_="LfshYc")
                if attr_tag is None:
                    attr_tag = detail.find("span", class_="_1i6OkT")
                if attr_tag is not None and name_tag is not None:
                    detail_shop[name_tag.text.lower().replace(" ", "_")] = attr_tag.text
        shop_information["thông_tin_chi_tiết"] = detail_shop
        self.shop_information = shop_information
        return self.shop_information

    # DETAIL INFORMATION
    def get_detail_information(self):
        dict_detail = {}
        soup = self.parse_html()
        box_element_detail = soup.find("div", class_="EZi7D0")
        if box_element_detail is None:
            self.detail_information = None
            return self.detail_information
        list_element_detail = box_element_detail.findAll("div", class_="VYmrqq")
        if not len(list_element_detail):
            self.detail_information = None
            return self.detail_information
        for each_detail_tag in list_element_detail:
            name_tag = each_detail_tag.find("label", class_="zgeHL-")
            attr_tag = each_detail_tag.find("div")
            if name_tag is not None and attr_tag is not None:
                if len(attr_tag.findAll("a")):
                    list_attr = [attr.text for attr in attr_tag.findAll("a")]
                    text = ">".join(list_attr)
                    dict_detail[name_tag.text.lower().replace(" ", "_")] = text
                else:
                    dict_detail[name_tag.text.lower().replace(" ", "_")] = attr_tag.text
        self.detail_information = dict_detail
        return self.detail_information

    def get_description(self):
        description = None
        soup = self.parse_html()
        element_description = soup.find("p", class_="N5VAH-")
        if element_description is None:
            self.description = description
            return self.description
        self.description = element_description.text
        return self.description

    def get_comments(self):
        list_comments = []
        soup = self.parse_html()
        box_comments = soup.findAll("div", class_="shopee-product-rating")
        if not len(box_comments):
            return self.comments
        for each in box_comments:
            each_comment = each.find("div", class_="EXI9SU")
            each_response = each.find("div", class_="mSKhgN")
            if each_comment is None:
                continue
            if each_response is None:
                list_comments.append({"comments": each_comment.get_text(strip=True, separator=" "), "reply": ""})
            else:
                list_comments.append({"comments": each_comment.get_text(strip=True, separator=" "),
                                      "reply": each_response.text})
        self.comments = list_comments
        return self.comments

    def get_image_link(self):
        if len(self.list_color_img):
            list_image_1 = [each[1] for each in self.list_color_img]
        else:
            list_image_1 = []
        soup = self.parse_html()
        list_image_2 = []
        box_images = soup.findAll("div", class_="Hl-jtg wdZ+2f")
        for each_box in box_images:
            src_img = each_box.get("style")
            src_img = self.parse_link_image(src_img).replace("_tn", "")
            list_image_2.append(src_img)
        list_diff = list(set(set(list_image_1) ^ set(list_image_2)))
        list_diff = [each for each in list_diff if each not in list_image_1]
        for i in range(len(list_diff)):
            name = "Unknown" + str(i)
            self.list_color_img.append((name, list_diff[i]))
        return self.list_color_img

    def get_video_link(self):
        list_video = []
        soup = self.parse_html()
        box_video = soup.find("div", class_="center _1fKb1T")
        if box_video is None:
            return
        tag_video = box_video.find("video")
        if tag_video is None:
            return
        src_video = tag_video.get("src")
        if src_video is not None:
            list_video.append(src_video)
        self.link_video = list_video

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
        javascript = "window.scrollBy(0,4000);"
        self.driver.execute_script(javascript)
        time.sleep(2)
        self.driver.execute_script(javascript)
        time.sleep(2)
        self.driver.execute_script(javascript)
        time.sleep(2)
        self.get_shop_information()
        self.get_detail_information()
        self.get_description()
        self.get_comments()
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
        if self.check_login_require():
            self.driver.close()
            return "VPN CHANGE"
        if self.check_available_web():
            self.driver.close()
            return "VPN CHANGE"
        self.extract_information()

        if self.main_information["name"] == "":
            # self.driver.close()
            return
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




