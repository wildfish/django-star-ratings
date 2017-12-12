from __future__ import division, unicode_literals

from django.test import override_settings
from django.contrib.auth import get_user_model
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from .testcase import SeleniumTestCase


class RateTest(SeleniumTestCase):
    def tearDown(self):
        self.logout()

    def test_user_is_not_logged_in___user_cannot_rate(self):
        self.driver.get(self.live_server_url)

        with self.assertRaises(NoSuchElementException):
            self.driver.find_element_by_xpath('//*[@data-score]').click()

    def test_click_star___rating_is_set_to_the_star_value(self):
        value = 3

        expected_percentage = 20 * value
        expected_style = 'width: {}%;'.format(expected_percentage)

        get_user_model().objects.create_user('user', password='pass')

        self.driver.get(self.live_server_url)

        self.login('user', 'pass')

        self.click_score(value)

        self.wait_for_user_to_equal(value)
        self.assertEqual(expected_style, str(self.foreground_elem.get_attribute('style')).strip())
        self.assertEqual(value, float(self.avg_rating_elem.text))
        self.assertEqual(1, int(self.count_elem.text))

    def test_star_rating_range_is_set___rating_range_on_page_is_the_star_rating(self):
        value = 3
        with override_settings(STAR_RATINGS_RANGE=value):
            self.driver.get(self.live_server_url)

            background = self.driver.find_element_by_class_name('star-ratings-rating-background')
            elements = background.find_elements_by_tag_name('li')

            self.assertEqual(value, len(elements))

    # remove the timeout on this test as it can take a while to run on remote browsers and there are no assumptions to
    # stop it finding examples
    def test_multiple_users_rate___average_count_and_user_are_correct(self):
        scores = [1, 2, 3]
        for i, score in enumerate(scores):
            self.driver.get(self.live_server_url)

            uname = 'user' + str(i)
            password = 'pass' + str(i)

            get_user_model().objects.create_user(
                username=uname,
                password=password,
            )

            self.login(uname, password)

            self.click_score(score)

            self.wait_for_user_to_equal(score)

            self.logout()

        expected_avg = sum(scores) / len(scores)
        self.assertAlmostEqual(expected_avg, float(self.avg_rating_elem.text), places=2)
        self.assertEqual(len(scores), int(self.count_elem.text))

    @override_settings(STAR_RATINGS_RERATE=True)
    def test_rerate_is_true___the_user_is_able_to_change_their_rating(self):
        values = [1, 2]
        first, second = values

        get_user_model().objects.create_user('user', password='pass')

        self.driver.get(self.live_server_url)

        self.login('user', 'pass')

        self.click_score(first)
        self.click_score(second)

        self.wait_for_user_to_equal(second)
        self.assertEqual(1, int(self.count_elem.text))

    @override_settings(STAR_RATINGS_RERATE=False)
    def test_rerate_is_false___the_user_is_not_able_to_change_their_rating(self):
        values = [1, 2]

        first, second = values

        get_user_model().objects.create_user('user', password='pass')

        self.driver.get(self.live_server_url)

        self.login('user', 'pass')

        self.click_score(first)
        self.wait_for_user_to_equal(first)
        self.click_score(second)

        self.assertEqual(1, int(self.count_elem.text))
        self.assertEqual(first, int(self.user_rating_elem.text))

    #
    # helper functions
    #

    @property
    def user_rating_elem(self):
        return self.driver.find_element_by_xpath('//*[@class="star-ratings-rating-user"]/*[@class="star-ratings-rating-value"]')

    @property
    def avg_rating_elem(self):
        return self.driver.find_element_by_xpath('//*[@class="star-ratings-rating-average"]/*[@class="star-ratings-rating-value"]')

    @property
    def count_elem(self):
        return self.driver.find_element_by_xpath('//*[@class="star-ratings-rating-count"]/*[@class="star-ratings-rating-value"]')

    @property
    def foreground_elem(self):
        return self.driver.find_element_by_class_name('star-ratings-rating-foreground')

    def wait_for_user_to_equal(self, value):
        try:
            WebDriverWait(self.driver, 30).until(lambda d: self.user_rating_elem.text == str(value))
        except TimeoutException:
            self.assertEqual(value, int(self.user_rating_elem.text))

    def click_score(self, score):
        try:
            if self.browser_tag and 'android_' in self.browser_tag:
                self.driver.find_element_by_xpath('//*[@class="star-ratings-rating-background"]//*[@data-score="{}"]/..'.format(score)).click()
            else:
                self.driver.find_element_by_xpath('//*[@class="star-ratings-rating-background"]//*[@data-score="{}"]'.format(score)).click()
        except WebDriverException:
            # if we aren't able to click the background this is most likely because the foreground is getting in the
            # way so try clicking that instead
            if self.browser_tag and 'android_' in self.browser_tag:
                self.driver.find_element_by_xpath('//*[@class="star-ratings-rating-foreground"]//*[@data-score="{}"]/..'.format(score)).click()
            else:
                self.driver.find_element_by_xpath('//*[@class="star-ratings-rating-foreground"]//*[@data-score="{}"]'.format(score)).click()

    def login(self, username, password):
        self.driver.find_element_by_id('login-link').click()
        self.driver.find_element_by_id('id_username').send_keys(username)
        self.driver.find_element_by_id('id_password').send_keys(password)
        self.driver.find_element_by_id('id_submit').click()

    def logout(self):
        with self.ignore_implicit_wait():
            try:
                self.driver.find_element_by_id('logout-link').click()
            except NoSuchElementException:
                pass
