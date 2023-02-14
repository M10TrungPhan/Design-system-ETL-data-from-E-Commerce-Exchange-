import time
import json
import os
import hashlib
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from objects.item import Item
from utils.utils import setup_selenium_firefox


class ItemTGDD(Item):

    def __init__(self, data_packet: dict, keyword: str, path_save_data: str):
        super(ItemTGDD, self).__init__(data_packet)
        self.url = data_packet["url"]
        self.id = self.item_id
        self.keyword = keyword.strip()
        self.path_save_data = path_save_data
        self.driver = None
        self.name = None
        self.main_information = None
        self.description = None
        self.technical_information = None
        self.comments = None

    @property
    def item_id(self):
        return hashlib.md5(str(self.url).encode("utf-8")).hexdigest()

    def access_website(self):
        self.driver = setup_selenium_firefox()
        try:
            self.driver.get(self.url)
        except:
            self.driver.close()
            return None
        time.sleep(3)
        return self.parse_html()

    def parse_html(self):
        return BeautifulSoup(self.driver.page_source, "lxml")

    # GET MAIN INFORMATION
    def get_main_information(self):
        main_information = {}
        soup = self.parse_html()
        # NAME
        name = ""
        name_tag = soup.find("h1")
        if name_tag is not None:
            name = name_tag.text.replace(" ", " ")
        main_information["name"] = name
        # PRICE
        original, present, discount = "", "", ""
        box_price = soup.find("div", class_="box-price")
        if box_price is not None:
            box_present = box_price.find("p", class_="box-price-present")
            if box_present is not None:
                present = box_present.text.replace(" ", " ")
            box_original = box_price.find("p", class_="box-price-old")
            if box_original is not None:
                original = box_original.text.replace(" ", " ")
            box_discount = box_price.find("p", class_="box-price-percent")
            if box_discount is not None:
                discount = box_discount.text.replace(" ", " ")
        price = {"giá_gốc": original, "giá_hiện_tại": present, "giảm_giá": discount}
        main_information["price"] = price
        # COLOR
        list_color = []
        box_color = soup.find("div", class_="box03 color group desk")
        if box_color is not None:
            list_tag_color = box_color.findAll("a")
            for tag in list_tag_color:
                list_color.append(tag.text.replace(" ", " "))
        main_information["color"] = list_color
        self.main_information = main_information
        return self.main_information

    # GET COMMENT
    def get_comment(self):
        list_tag = self.get_all_list_tag_comment()
        list_comment = []
        for tag in list_tag:
            list_comment.append(self.get_content_comment(tag))
        self.comments = list_comment
        return self.comments

    def get_all_list_tag_comment(self):
        javascript = "window.scrollBy(0,4000);"
        self.driver.execute_script(javascript)
        time.sleep(1)
        list_tag_comment = self.get_list_tag_in_page()
        try:
            list_btn_next = self.driver.find_element(By.CLASS_NAME, "pagcomment").find_elements(By.TAG_NAME, "a")
        except:
            return list_tag_comment

        while True:
            list_btn_next[-1].click()
            time.sleep(1)
            a = list_btn_next[-1]
            time.sleep(1)
            list_tag_comment = list_tag_comment + self.get_list_tag_in_page()
            list_btn_next = self.driver.find_element(By.CLASS_NAME, "pagcomment").find_elements(By.TAG_NAME, "a")
            if len(list_btn_next) < 6:
                list_btn_next[-1].click()
                time.sleep(1)
                list_tag_comment = list_tag_comment + self.get_list_tag_in_page()
                break
            if a == list_btn_next[-1]:
                break
        return list_tag_comment

    def get_list_tag_in_page(self):
        try:
            self.driver.find_element(By.CLASS_NAME, "fullcomment").click()
        except:
            pass
        try:
            self.driver.find_element(By.CLASS_NAME, "viewMore").click()
        except NoSuchElementException:
            pass
        soup = self.parse_html()
        list_tag = soup.findAll("li", class_="comment_ask")
        return list_tag

    @staticmethod
    def get_content_comment(tag):
        dialog = []
        user = tag.find("div", class_="rowuser").find("a").find("strong").text.replace(" ", " ")
        speech = tag.find("div", class_="question").get_text(". ", strip=True).replace("..", ".").replace(",.", ".").replace(" ", " ")
        dialog.append({"user_name": user, "text": speech})
        box_list_reply = tag.find("div", class_="listreply")
        list_reply = box_list_reply.findAll("div", class_="reply")
        for reply in list_reply:
            user = reply.find("div", class_="rowuser").find("strong").get_text(". ", strip=True).replace("..", ".").replace(",.", ".").replace(" ", " ")
            speech = reply.find("div", class_="cont").get_text(". ", strip=True).replace("..", ".").replace(",.", ".").replace(" ", " ")
            dialog.append({"user_name": user, "text": speech})
        return dialog

    # GET DETAIL INFORMATION
    def get_description_information(self):
        javascript = "window.scrollBy(0,2000);"
        self.driver.execute_script(javascript)
        try:
            self.driver.find_element(By.CLASS_NAME, "btn-detail.jsArticle").click()
        except:
            self.description = self.get_description_information_2()
            return self.description
        time.sleep(4)
        soup = self.parse_html()
        box_content = soup.find("div", class_="content-article")
        a = box_content.findChild()
        content = a.get_text(strip=True).replace("..", ".").replace(",.", ".").replace(" ", " ") + "\n"
        while True:
            a = a.find_next_sibling()
            if a is None:
                break
            if a.find("i") is None:
                text = a.get_text(". ", strip=True).replace("..", ".").replace(",.", ".").replace(" ", " ")
                if text != "":
                    content += text + "\n"
        try:
            self.driver.find_element(By.CLASS_NAME, "btn-closemenu.close-tab").click()
        except:
            pass
        self.description = content
        return self.description

    def get_description_information_2(self):
        soup = self.parse_html()
        box_detail = soup.find("div", class_="short-article")
        if box_detail is None:
            return None
        self.description = box_detail.get_text(". ", strip=True).replace("..", ".").replace(",.", ".").replace(" ", " ")
        return self.description

    # GET TECHNICAL INFROMATION
    def get_technical_information(self):
        elements = []
        box_technical = None
        for _ in range(5):
            try:
                self.driver.find_element(By.CLASS_NAME, "btn-detail.btn-short-spec ").click()
            except:
                try:
                    self.driver.find_element(By.CLASS_NAME, "btn-detail.btn-short-spec.not-have-instruction").click()
                except:
                    pass
            time.sleep(3)
            soup = self.parse_html()
            box_technical = soup.find("div", class_="parameter-all")
            if box_technical is not None:
                break
            self.driver.get(self.url)
        if box_technical is None:
            self.technical_information = self.get_technical_information_2()
            return self.technical_information
        # self.driver.find_element(By.CLASS_NAME, "btn-detail.jsArticle").click()
        # time.sleep(3)
        # self.driver.find_element(By.ID, "tab-specification-gallery-0").click()
        time.sleep(3)
        list_elements = box_technical.findAll("div", class_="parameter-item")
        for el in list_elements:
            list_attr = []
            name_el = el.find("p", class_= "parameter-ttl")
            if name_el is not None:
                name_el = name_el.get_text(". ", strip=True).replace("..", ".").replace(",.", ".").replace(" ", " ")
            else:
                name_el = "Thông số chung"
            list_attr_el = el.findAll("li")
            for attr in list_attr_el:
                left = attr.find("div", class_="ctLeft").text.replace("\n", "")
                right = attr.find("div", class_="ctRight")
                circle_tag = right.findAll("p", class_="circle")
                if not len(circle_tag):
                    list_attr.append({left: [right.text.replace("\n", "").replace(" ", " ").rstrip()]})
                else:
                    list_cir = []
                    for cir in circle_tag:
                        list_cir.append(cir.text.replace("\n", "").replace(" ", " ").rstrip())
                    list_attr.append({left: list_cir})
            elements.append({"name_element": name_el, "attr": list_attr})
        self.driver.find_element(By.CLASS_NAME, "btn-closemenu.close-tab").click()
        self.technical_information = elements
        return self.technical_information

    def get_technical_information_2(self):
        name_el = "Thông số chung"
        list_attr = []
        soup = self.parse_html()
        box_technical = soup.find("div", class_="parameter")
        if box_technical is None:
            return None
        list_attr_tag = box_technical.find("ul").findAll("li")
        for attr in list_attr_tag:
            left = attr.find("p", class_="lileft").get_text(". ", strip=True).replace("..", ".").replace(",.", ".").replace(" ", " ")
            right = attr.find("div", class_="liright").get_text(". ", strip=True).replace("..", ".").replace(",.", ".").replace(" ", " ")
            list_attr.append({left: right})
        self.technical_information = {"name_element": name_el, "attr": list_attr}
        return self.technical_information

    @property
    def dict_data(self):
        return {"_id": self.id,
                "url": self.url,
                "keyword": self.keyword,
                "main_information": self.main_information,
                "technical_information": self.technical_information,
                "description": self.description,
                "comments": self.comments
                }

    def save_text(self):
        file_data_folder = self.path_save_data + self.keyword + "/text/" + self.id
        if self.main_information is None:
            print("EROOR TGDD")
            return
        path_text = self.path_save_data + self.keyword + "/text"
        os.makedirs(path_text, exist_ok= True)
        json.dump(self.dict_data, open(file_data_folder + ".json", "w", encoding="utf-8"),
                  ensure_ascii=False, indent=4)

    def extract_data(self):
        access = self.access_website()
        if access is None:
            self.driver.close()
            return
        self.get_main_information()
        self.get_description_information()
        if self.description is None:
            self.driver.close()
            return
        self.get_technical_information()
        self.get_comment()
        self.save_text()
        print(f"Save {self.url}")
        self.driver.close()












