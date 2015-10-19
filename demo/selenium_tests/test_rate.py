from time import sleep
from django.contrib.auth import get_user_model
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .testcase import SeleniumTestCase


class RateTest(SeleniumTestCase):
    def login(self, wait, username, password):
        wait.until(EC.presence_of_element_located((By.ID, 'login-link'))).click()
        wait.until(EC.presence_of_element_located((By.ID, 'id_username'))).send_keys(username)
        wait.until(EC.presence_of_element_located((By.ID, 'id_password'))).send_keys(password)
        wait.until(EC.presence_of_element_located((By.ID, 'id_submit'))).click()

    def test_click_first_star___rating_is_set_to_one(self, driver):
        get_user_model().objects.create_user('user', password='pass')

        driver.get(self.live_server_url)

        wait = WebDriverWait(driver, 30)
        self.login(wait, 'user', 'pass')

        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@data-score="1"]'))).click()

        foreground = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'star-ratings-rating-foreground')))
        average_elem = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@class="star-ratings-rating-average"]/*[@class="star-ratings-rating-value"]')))
        count_elem = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@class="star-ratings-rating-count"]/*[@class="star-ratings-rating-value"]')))
        user_elem = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@class="star-ratings-rating-user"]/*[@class="star-ratings-rating-value"]')))

        self.assertEqual('width: 20%;', str(foreground.get_attribute('style')).strip())
        self.assertEqual('1.00', average_elem.text)
        self.assertEqual('1', count_elem.text)
        self.assertEqual('1', user_elem.text)
