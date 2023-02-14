import re
import time
import os
import requests

from selenium.webdriver.common.by import By
from objects.item import Item
from config.config import Config
from selenium.common.exceptions import NoSuchElementException



class ItemShopee(Item):

    def __init__(self, url: str, key: str):
        super(ItemShopee, self).__init__(url)
        self.key = key
        self.config = Config()
        self.driver = None
        self.main_information = None
        self.shop_information = None
        self.detail_information = None
        self.description = None
        self.comments = None
        self.image = []
        self.video = []

    # MAIN INFORMATION
    def get_main_information(self):
        main_information = {}
        try:
            element_name = self.driver.find_element(by=By.CLASS_NAME, value="VCNVHn")
            main_information["name"] = element_name.text.replace("\n", ". ")
        except NoSuchElementException:
            main_information["name"] = ""

        # PRICE
        try:
            original_price = self.driver.find_element(by=By.CLASS_NAME, value="CDN0wz").text
        except NoSuchElementException:
            original_price = ""
        try:
            current_price = self.driver.find_element(by=By.CLASS_NAME, value="pmmxKx").text
        except NoSuchElementException:
            current_price = ""
        try:
            discount = self.driver.find_element(by=By.CLASS_NAME, value="lTuS3S").text
        except NoSuchElementException:
            discount = ""
        price = {"giá_gốc": original_price, "giá_hiện_tại": current_price, "giảm_giá": discount}
        main_information["price"] = price
        # COLOR/SIZE
        try:
            box_attribute = self.driver.find_element(by=By.CLASS_NAME, value="PMuAq5")
            list_attribute = box_attribute.find_elements(by=By.CLASS_NAME, value="flex.items-center")
            for attr in list_attribute:
                list_var = []
                try:
                    name = attr.find_element(by=By.CLASS_NAME, value="_0b8hHE").text.lower().replace(" ", "_")
                    try:
                        list_variation = attr.find_elements(by=By.CLASS_NAME, value="product-variation")
                        for var in list_variation:
                            list_var.append(var.text)
                        if len(list_var):
                            main_information[name] = list_var
                    except NoSuchElementException:
                        continue
                except NoSuchElementException:
                    continue
        except NoSuchElementException:
            pass
        return main_information

# SHOP INFORMATION
    def get_shop_information(self):
        shop_information = {}
        try:
            box_shop = self.driver.find_element(by=By.CLASS_NAME, value="JfALJ-.page-product__shop")
        except NoSuchElementException:
            return None
        try:
            shop_name = box_shop.find_element(by=By.CLASS_NAME, value="_6HeM6T").text
        except NoSuchElementException:
            shop_name = ""
        shop_information["tên_shop"] = shop_name
        detail_shop = {}
        try:
            box_detail = box_shop.find_element(by=By.CLASS_NAME, value="biYJq8")
            list_element_detail = []
            try:
                list_element_detail = box_detail.find_elements(by=By.CLASS_NAME, value="pHNb7U.cgFEJd")

                try:
                    list_element_detail.append(box_detail.find_element(by=By.CLASS_NAME, value="Um7a0Z.cgFEJd"))
                except NoSuchElementException:
                    pass
            except NoSuchElementException:
                pass
            if len(list_element_detail):
                for detail in list_element_detail:
                    detail_text = detail.text
                    start, end = re.search("\n", detail_text).span()
                    name = detail_text[0:start].lower().replace(" ", "_")
                    attr = detail_text[end:]
                    detail_shop[name] = attr
        except NoSuchElementException:
            pass
        shop_information["thông_tin_chi_tiết"] = detail_shop
        return shop_information

# DETAIL INFORMATION
    def get_detail_information(self):
        dict_detail = {}
        try:
            box_element_detail = self.driver.find_element(by=By.CLASS_NAME, value="""KqLK01""")
        except NoSuchElementException:
            return dict_detail
        list_element_detail = box_element_detail.find_elements(by=By.CLASS_NAME, value="_3Xk7SJ")
        for each_detail in list_element_detail:
            detail_information = each_detail.text
            if re.search("\n", detail_information) is not None:
                start, end = re.search("\n", detail_information).span()
                dict_detail[detail_information[0:start].lower().replace(" ", "_")] = detail_information[end:]\
                    .replace("\n", ">")
            else:
                pass
        return dict_detail

# DESCRIPTION
    def get_description(self):
        try:
            element_description = self.driver.find_element(by=By.CLASS_NAME, value="""hrQhmh""")
            description = element_description.text
            return description
        except NoSuchElementException:
            return ""

    def get_comments(self):
        list_comments = []
        box_comments = self.driver.find_elements(by=By.CLASS_NAME, value="shopee-product-rating__main")
        for each in box_comments:
            try:
                each_comments = each.find_element(by=By.CLASS_NAME, value="Em3Qhp")
                comments = each_comments.get_text(strip=True, separator=" ")
            except NoSuchElementException:
                continue
            try:
                each_response = each.find_element(by=By.CLASS_NAME, value="gGF2-r")
                response = each_response.text
                start, end = re.search("\n", response).span()
                response = response[end:]
            except NoSuchElementException:
                response = ""
            list_comments.append({"comments": comments, "reply": response})
        # print(list_comments)
        return list_comments

    def get_image(self):
        box_images = self.driver.find_elements(by=By.CLASS_NAME, value="y1rHjh")
        list_images = []
        list_dir_img = []
        for each in box_images:
            div_image = each.find_element(by=By.CLASS_NAME, value="Mzs0kz")
            style = div_image.find_element(by=By.TAG_NAME, value="div").get_attribute("style")
            if style != "":
                _, start = re.search(r"""[(]["]""", style).span()
                end, _ = re.search(r"""["][)]""", style).span()
                list_images.append(style[start:end])

        folder_name = self.config.dir_folder_data_image + self.key + "/" + self.id
        if self.id not in os.listdir(self.config.dir_folder_data_image + self.key + "/"):
            os.makedirs(folder_name)
        for i in range(len(list_images)):
            dir_img = self.config.folder_data_image + self.key + "/" + self.id + "/" + str(i) + '.jpg'
            filename = self.config.dir_folder_data_image + self.key + "/" + self.id + "/" + str(i) + '.jpg'
            img = list_images[i]
            list_dir_img.append(dir_img)
            while str(i) + '.jpg' not in os.listdir(self.config.dir_folder_data_image +
                                                    self.key + "/" + self.id + "/"):
                with open(filename, 'wb') as f:
                    f.write(requests.get(img).content)
        return list_dir_img

    def get_video(self):
        box = self.driver.find_element(by=By.CLASS_NAME, value="center.ZCd4YG")
        box_videos = box.find_element(by=By.TAG_NAME, value="video")
        src_video = box_videos.get_attribute("src")
        folder_name = self.config.dir_folder_data_video + self.key + "/" + self.id
        if src_video == "":
            return []
        if self.id not in os.listdir(self.config.dir_folder_data_video + self.key + "/"):
            os.makedirs(folder_name)
        filename = self.config.dir_folder_data_video + self.key + "/" + self.id + "/" + "video.mp4"
        dir_video = self.config.folder_data_video + self.key + "/" + self.id + "/" + "video.mp4"
        with open(filename, 'wb') as f:
            f.write(requests.get(src_video).content)
        return [dir_video]

    def check_login_require(self):
        try:
            self.driver.find_element(by=By.CLASS_NAME, value="K1dDgL")
            return False
        except NoSuchElementException:
            return True
        except:
            return True

    def extract_data(self):
        # time.sleep(3)
        self.main_information = ""
        for _ in range(5):
            self.main_information = self.get_main_information()
            if self.main_information["name"] != "":
                break
        if self.main_information["name"] != "":
            javascript = "window.scrollBy(0,4000);"
            self.driver.execute_script(javascript)
            time.sleep(2)
            self.driver.execute_script(javascript)
            time.sleep(2)
            self.driver.execute_script(javascript)
            self.shop_information = self.get_shop_information()
            self.detail_information = self.get_detail_information()
            self.description = self.get_description()
            self.comments = self.get_comments()
            self.get_image()
            self.get_video()
            return True
        return False

    @property
    def dict_data(self):
        return{"_id": self.id,
               "url": self.url,
               "main_information": self.main_information,
               "shop_information": self.shop_information,
               "detail": self.detail_information,
               "description": self.description,
               "comments": self.comments,
               "image": self.image,
               "video": self.video}
