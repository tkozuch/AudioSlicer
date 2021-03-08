import os

try:
    browser_driver = os.environ['BROWSER_DRIVER']
except KeyError:
    raise ValueError("BROWSER_DRIVER env variable not specified. \nPlease specify path to your "
                     "browsers driver, more information: "
                     "https://selenium-python.readthedocs.io/installation.html#drivers")

os.environ["PATH"] += browser_driver

from django.contrib.staticfiles.testing import LiveServerTestCase
from selenium import webdriver


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

    def test_slicing_is_possible_after_adding_and_subtracting_custom_slicing_info(self):
        self.selenium.get('http://127.0.0.1:8000/')
        self._delete_all_possible_inputs()
        self._add_n_inputs(2)
        file = os.path.join(os.getcwd(), 'slicing_app', 'tests', 'test_album_shorter.mp3')
        self._choose_file(file)

        pass

    def _delete_all_possible_inputs(self):
        inputs_divs = self.selenium.find_elements_by_class_name('title-time-info')
        for i in range(inputs_divs.length - 2):
            subtract_button = inputs_divs[i].find_element_by_tag_name('button')
            subtract_button.click()

    def _add_n_inputs(self, n):
        add_button = self.selenium.find_element_by_id('add-button')
        for i in range(n):
            add_button.click()

    def _choose_file(self, file_path):
        file_input = self.selenium.find_element_by_id('id_file')
        file_input.send_keys(file_path)
