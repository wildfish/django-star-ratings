from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from hypothesis import given
from hypothesis.extra.django import TestCase
from hypothesis.strategies import integers
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class RateTest(TestCase, StaticLiveServerTestCase):
    def login(self, wait, username, password):
        wait.until(EC.presence_of_element_located((By.ID, 'login-link'))).click()
        wait.until(EC.presence_of_element_located((By.ID, 'id_username'))).send_keys(username)
        wait.until(EC.presence_of_element_located((By.ID, 'id_password'))).send_keys(password)
        wait.until(EC.presence_of_element_located((By.ID, 'id_submit'))).click()

    def logout(self, wait):
        try:
            wait.until(EC.presence_of_element_located((By.ID, 'logout-link'))).click()
        except TimeoutException:
            pass

    def tearDown(self):
        self.logout(WebDriverWait(self.driver, 30))

    @given(integers(min_value=1, max_value=5))
    def test_click_first_star___rating_is_set_to_one(self, value):
        expected_percentage = 20 * value
        expected_style = 'width: {}%;'.format(expected_percentage)

        get_user_model().objects.create_user('user', password='pass')

        self.driver.get(self.live_server_url)

        wait = WebDriverWait(self.driver, 30)
        self.login(wait, 'user', 'pass')

        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@data-score="{}"]'.format(value)))).click()

        foreground = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'star-ratings-rating-foreground')))
        average_elem = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@class="star-ratings-rating-average"]/*[@class="star-ratings-rating-value"]')))
        count_elem = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@class="star-ratings-rating-count"]/*[@class="star-ratings-rating-value"]')))
        user_elem = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@class="star-ratings-rating-user"]/*[@class="star-ratings-rating-value"]')))

        self.assertEqual(expected_style, str(foreground.get_attribute('style')).strip())
        self.assertEqual(value, float(average_elem.text))
        self.assertEqual(1, int(count_elem.text))
        self.assertEqual(value, int(user_elem.text))
