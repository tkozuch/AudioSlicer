import os

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver


class TestMostCommonUserActions(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        try:
            browser_driver = os.environ["BROWSER_DRIVER"]
        except KeyError:
            raise ValueError(
                "BROWSER_DRIVER env variable not specified. \nPlease specify path to your "
                "browsers driver, more information: "
                "https://selenium-python.readthedocs.io/installation.html#drivers"
            )

        os.environ["PATH"] += browser_driver
        super().setUpClass()
        cls.selenium = webdriver.Chrome()
        cls.selenium.implicitly_wait(10)

        if settings.DEBUG is False:
            settings.DEBUG = True

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_page_rendered(self):
        self.selenium.get(self.live_server_url)
        self.selenium.find_element_by_xpath('//a[contains(text(),"Audio Slicer")]')
        self.selenium.find_element_by_xpath('//button[contains(text(), "Slice")]')

    def test_user_is_able_to_substract_inputs(self):
        self.selenium.get(self.live_server_url)
        self._delete_all_possible_inputs()

    def test_user_is_able_to_add_inputs(self):
        self.selenium.get(self.live_server_url)
        self._add_n_inputs(2)

    def test_user_is_able_to_choose_file(self):
        self.selenium.get(self.live_server_url)
        file = os.path.join(
            os.getcwd(), "slicing_app", "tests", "test_album_shorter.mp3"
        )
        self._choose_file(file)

    def _delete_all_possible_inputs(self):
        inputs_divs = self.selenium.find_elements_by_class_name("title-time-info")
        for i in range(len(inputs_divs) - 2):
            subtract_button = inputs_divs[i].find_element_by_tag_name("button")
            subtract_button.click()

    def _add_n_inputs(self, n):
        add_button = self.selenium.find_element_by_id("add-button")
        for i in range(n):
            add_button.click()

    def _choose_file(self, file_path):
        file_input = self.selenium.find_element_by_id("id_file")
        file_input.send_keys(file_path)
