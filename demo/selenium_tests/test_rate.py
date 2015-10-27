from django.test import override_settings
from mock import patch
from django.contrib.auth import get_user_model
from hypothesis import given, settings
from hypothesis.extra.django import TestCase
from hypothesis.strategies import integers, lists
from selenium.common.exceptions import NoSuchElementException
from .testcase import SeleniumTestCase


class RateTest(TestCase, SeleniumTestCase):
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

    def tearDown(self):
        self.logout()

    def test_user_is_not_logged_in___user_cannot_rate(self):
        self.driver.get(self.live_server_url)

        with self.assertRaises(NoSuchElementException):
            self.driver.find_element_by_xpath('//*[@data-score]').click()

    @given(integers(min_value=1, max_value=5))
    def test_click_first_star___rating_is_set_to_one(self, value):
        expected_percentage = 20 * value
        expected_style = 'width: {}%;'.format(expected_percentage)

        get_user_model().objects.create_user('user', password='pass')

        self.driver.get(self.live_server_url)

        self.login('user', 'pass')

        self.driver.find_element_by_xpath('//*[@data-score="{}"]'.format(value)).click()

        foreground = self.driver.find_element_by_class_name('star-ratings-rating-foreground')
        average_elem = self.driver.find_element_by_xpath('//*[@class="star-ratings-rating-average"]/*[@class="star-ratings-rating-value"]')
        count_elem = self.driver.find_element_by_xpath('//*[@class="star-ratings-rating-count"]/*[@class="star-ratings-rating-value"]')
        user_elem = self.driver.find_element_by_xpath('//*[@class="star-ratings-rating-user"]/*[@class="star-ratings-rating-value"]')

        self.assertEqual(expected_style, str(foreground.get_attribute('style')).strip())
        self.assertEqual(value, float(average_elem.text))
        self.assertEqual(1, int(count_elem.text))
        self.assertEqual(value, int(user_elem.text))

    @given(integers(min_value=1, max_value=10))
    def test_star_rating_range_is_set___rating_range_on_page_is_the_star_rating(self, value):
        with patch('star_ratings.templatetags.ratings.STAR_RATINGS_RANGE', value):
            self.driver.get(self.live_server_url)

            background = self.driver.find_element_by_class_name('star-ratings-rating-background')
            elements = background.find_elements_by_tag_name('li')

            self.assertEqual(value, len(elements))

    # remove the timeout on this test as it can take a while to run on remote browsers and there are no assumptions to
    # stop it finding examples
    @given(lists(integers(min_value=1, max_value=5), min_size=2, max_size=10), settings=settings.Settings(max_examples=10, timeout=0))
    def test_multiple_users_rate___average_count_and_user_are_correct(self, scores):
        for i, score in enumerate(scores):
            uname = 'user' + str(i)
            password = 'pass' + str(i)

            get_user_model().objects.create_user(
                username=uname,
                password=password,
            )

            self.login(uname, password)

            self.driver.find_element_by_xpath('//*[@data-score="{}"]'.format(score)).click()

            user_elem = self.driver.find_element_by_xpath('//*[@class="star-ratings-rating-user"]/*[@class="star-ratings-rating-value"]')
            self.assertEqual(score, int(user_elem.text))

            self.logout()

        average_elem = self.driver.find_element_by_xpath('//*[@class="star-ratings-rating-average"]/*[@class="star-ratings-rating-value"]')
        count_elem = self.driver.find_element_by_xpath('//*[@class="star-ratings-rating-count"]/*[@class="star-ratings-rating-value"]')

        expected_avg = sum(scores) / len(scores)
        self.assertAlmostEqual(expected_avg, float(average_elem.text), places=2)
        self.assertEqual(len(scores), int(count_elem.text))

    @override_settings(STAR_RATINGS_RERATE=True)
    @given(lists(integers(min_value=1, max_value=5), unique_by=lambda x: x, min_size=2, max_size=2), settings=settings.Settings(max_examples=10))
    def test_rerate_is_true___the_user_is_able_to_change_their_rating(self, values):
        first, second = values

        get_user_model().objects.create_user('user', password='pass')

        self.driver.get(self.live_server_url)

        self.login('user', 'pass')

        self.driver.find_element_by_xpath('//*[@data-score="{}"]'.format(first)).click()
        self.driver.find_element_by_xpath('//*[@data-score="{}"]'.format(second)).click()

        count_elem = self.driver.find_element_by_xpath('//*[@class="star-ratings-rating-count"]/*[@class="star-ratings-rating-value"]')
        user_elem = self.driver.find_element_by_xpath('//*[@class="star-ratings-rating-user"]/*[@class="star-ratings-rating-value"]')
        self.assertEqual(1, int(count_elem.text))
        self.assertEqual(second, int(user_elem.text))

    @override_settings(STAR_RATINGS_RERATE=False)
    @given(lists(integers(min_value=1, max_value=5), unique_by=lambda x: x, min_size=2, max_size=2), settings=settings.Settings(max_examples=10))
    def test_rerate_is_false___the_user_is_not_able_to_change_their_rating(self, values):
        first, second = values

        get_user_model().objects.create_user('user', password='pass')

        self.driver.get(self.live_server_url)

        self.login('user', 'pass')

        self.driver.find_element_by_xpath('//*[@data-score="{}"]'.format(first)).click()
        self.driver.find_element_by_xpath('//*[@data-score="{}"]'.format(second)).click()

        count_elem = self.driver.find_element_by_xpath('//*[@class="star-ratings-rating-count"]/*[@class="star-ratings-rating-value"]')
        user_elem = self.driver.find_element_by_xpath('//*[@class="star-ratings-rating-user"]/*[@class="star-ratings-rating-value"]')
        self.assertEqual(1, int(count_elem.text))
        self.assertEqual(first, int(user_elem.text))
