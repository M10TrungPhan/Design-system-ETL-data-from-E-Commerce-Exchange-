import logging


class WebCrawlBySearch:

    def __init__(self, keyword, path_save_data):
        self.path_save_data = path_save_data
        self.keyword = keyword

    def get_keyword_encoded(self):
        pass

    def get_number_total_item(self):
        pass

    def get_number_total_page(self):
        pass

    def request_html(self, url):
        pass

    def request_html_by_api(self, url):
        pass

    def get_link_in_page(self, *args):
        pass

    def get_link_in_page_api(self, page):
        pass

    def get_link_for_key(self):
        pass

    def load_list_item_crawled(self):
        pass

    def load_list_id(self):
        pass

    @property
    def payload(self):
        return




