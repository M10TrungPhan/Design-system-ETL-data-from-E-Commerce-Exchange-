import os

from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.proxy import ProxyType, Proxy

from common.common_keys import *
from objects.singleton import Singleton


class Config(metaclass=Singleton):
    mongodb_host = os.getenv(MONGODB_HOST, '172.28.0.23')
    mongodb_port = int(os.getenv(MONGODB_PORT, '20253'))
    mongodb_username = os.getenv(MONGODB_USERNAME, 'admin')
    mongodb_password = os.getenv(MONGODB_PASSWORD, 'admin')
    data_shopee_database = os.getenv(DATA_SHOPEE_DATABASE, "shopee")
    data_shopee_collection = os.getenv(DATA_SHOPEE_COLLECTION, "item")
    logging_folder = 'log'
    logging_name = "crawler.log"
    number_crawler = 5
    memory = "D:/trungphan/"
    folder_data_text = "Data/shopee/text/"
    folder_data_image = "Data/shopee/image/"
    folder_data_video = "Data/shopee/video/"
    dir_folder_data_text = memory + folder_data_text
    dir_folder_data_image = memory + folder_data_image
    dir_folder_data_video = memory + folder_data_video
    time_sleep_after_crawl = 10
    time_add_key_periodic = 3600

    def __init__(self):
        self.driver = None

    @staticmethod
    def setup_selenium_chrome():
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--test-type")
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('disable-infobars')
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_argument("--incognito")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.headless = True
        ser = Service("chromedriver_win32/chromedriver.exe")
        prox = "localhost:8080"
        proxy = Proxy()
        proxy.proxy_type = ProxyType.MANUAL
        proxy.http_proxy = prox
        capabilities = webdriver.DesiredCapabilities.CHROME
        proxy.add_to_capabilities(capabilities)
        driver = webdriver.Chrome(service=ser,
                                  options=chrome_options,
                                  desired_capabilities=capabilities)
        return driver

    @staticmethod
    def setup_selenium_firefox():
        ser = Service("chromedriver_win32/geckodriver.exe")
        firefox_options = FirefoxOptions()
        firefox_options.set_preference('devtools.jsonview.enabled', False)
        firefox_options.add_argument("--test-type")
        firefox_options.add_argument('--ignore-certificate-errors')
        firefox_options.add_argument('--disable-extensions')
        firefox_options.add_argument('disable-infobars')
        firefox_options.add_argument("--incognito")
        firefox_options.add_argument("--headless")
        driver = webdriver.Firefox(service=ser, options=firefox_options)
        return driver
