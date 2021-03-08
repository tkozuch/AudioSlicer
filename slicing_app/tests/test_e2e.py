import os

from django.contrib.staticfiles.testing import LiveServerTestCase
from selenium import webdriver

try:
    browser_driver = os.environ["BROWSER_DRIVER"]
except KeyError:
    raise ValueError(
        "BROWSER_DRIVER env variable not specified. \nPlease specify path to your "
        "browsers driver, more information: "
        "https://selenium-python.readthedocs.io/installation.html#drivers"
    )

os.environ["PATH"] += browser_driver


class TestMostCommonUserActions(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_page_rendered(self):
        # Fixme: To be changed to LiveServerTestCase url.
        self.selenium.get("http://127.0.0.1:8000/")
        self.selenium.find_element_by_xpath('//a[contains(text(),"Audio Slicer")]')
        self.selenium.find_element_by_xpath('//button[contains(text(), "Slice")]')

    def test_user_is_able_to_substract_inputs(self):
        self.selenium.get("http://127.0.0.1:8000/")
        self._delete_all_possible_inputs()

    def test_user_is_able_to_add_inputs(self):
        self.selenium.get("http://127.0.0.1:8000/")
        self._add_n_inputs(2)

    def test_user_is_able_to_choose_file(self):
        self.selenium.get("http://127.0.0.1:8000/")
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
