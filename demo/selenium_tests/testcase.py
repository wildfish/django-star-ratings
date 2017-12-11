from __future__ import unicode_literals

import os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver

_sauce_username = os.environ.get('SAUCE_USERNAME', None)
_sauce_access_key = os.environ.get('SAUCE_ACCESS_KEY', None)
_travis_job_number = os.environ.get('TRAVIS_JOB_NUMBER', None)
_branch_name = os.environ.get('TRAVIS_BRANCH', 'No Branch')
_browser_tag = os.environ.get('BROWSER_TAG', None)
_use_remote_driver = _browser_tag is not None

_remote_browsers = {
    'chrome_latest': {
        'platform': 'Linux',
        'browserName': 'chrome',
        'version': '',
    },
    'firefox_latest': {
        'platform': 'Linux',
        'browserName': 'firefox',
        'version': '',
    },
    'opera_latest': {
        'platform': 'Linux',
        'browserName': 'opera',
        'version': '',
    },
    'edge_latest': {
        'platform': 'Windows 10',
        'browserName': 'microsoftedge',
        'version': '',
    },
    'ie_11': {
        'platform': 'Windows 10',
        'browserName': 'internet explorer',
        'version': '11',
    },
    'ie_10': {
        'platform': 'Windows 8',
        'browserName': 'internet explorer',
        'version': '10',
    },
    'ie_9': {
        'platform': 'Windows 7',
        'browserName': 'internet explorer',
        'version': '9',
    },
    'safari_latest': {
        'platform': 'Mac OS X 10.11',
        'browserName': 'safari',
        'version': '',
    },
    'android_5.1': {
        'platform': 'Linux',
        'browserName': 'android',
        'deviceName': 'Android Emulator',
        'version': '5.1',
    },
    'android_5.0': {
        'platform': 'Linux',
        'browserName': 'android',
        'deviceName': 'Android Emulator',
        'version': '5.0',
    },
    'android_4.4': {
        'platform': 'Linux',
        'browserName': 'android',
        'deviceName': 'Android Emulator',
        'version': '4.4',
    },
    'android_4.3': {
        'platform': 'Linux',
        'browserName': 'android',
        'deviceName': 'Android Emulator',
        'version': '4.3',
    },
    'android_4.2': {
        'platform': 'Linux',
        'browserName': 'android',
        'deviceName': 'Android Emulator',
        'version': '4.2',
    },
    'android_4.1': {
        'platform': 'Linux',
        'browserName': 'android',
        'deviceName': 'Android Emulator',
        'version': '4.1',
    },
    'iphone_latest': {
        'platform': 'OS X 10.10',
        'browserName': 'iPhone',
        'deviceName': 'iPhone Simulator',
        'version': '',
    },
    'iphone_8.4': {
        'platform': 'OS X 10.10',
        'browserName': 'iPhone',
        'deviceName': 'iPhone Simulator',
        'version': '8.4',
    },
    'ipad_latest': {
        'platform': 'OS X 10.10',
        'browserName': 'iPhone',
        'deviceName': 'iPad Simulator',
        'version': '',
    },
    'ipad_8.4': {
        'platform': 'OS X 10.10',
        'browserName': 'iPhone',
        'deviceName': 'iPad Simulator',
        'version': '8.4',
    }
}


class IgnoreImplicitWait:
    def __init__(self, driver, default_wait):
        self._driver = driver
        self._default_wait = default_wait

        self._driver.implicitly_wait(0)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._driver.implicitly_wait(self._default_wait)


class SeleniumTestCase(StaticLiveServerTestCase):
    selenium_implicit_wait = 30
    _driver = None

    def __init__(self, *args, **kwargs):
        self.browser_tag = _browser_tag
        super(SeleniumTestCase, self).__init__(*args, **kwargs)

    @classmethod
    def setUpClass(cls):
        if not SeleniumTestCase._driver:
            if _use_remote_driver:
                sauce_url = 'http://%s:%s@ondemand.saucelabs.com:80/wd/hub' % (_sauce_username, _sauce_access_key)
                browser = _remote_browsers[_browser_tag]
                browser['tunnelIdentifier'] = _travis_job_number
                browser['build'] = _travis_job_number
                browser['tags'] = [_browser_tag, _branch_name]
                browser['name'] = '{} {} {}'.format(_travis_job_number, _browser_tag, _branch_name)

                SeleniumTestCase._driver = webdriver.Remote(
                    desired_capabilities=browser,
                    command_executor=sauce_url
                )
            else:
                SeleniumTestCase._driver = webdriver.Chrome()

            SeleniumTestCase._driver.implicitly_wait(cls.selenium_implicit_wait)

        super(SeleniumTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.cleanup_browser()
        super(SeleniumTestCase, cls).tearDownClass()

    @property
    def driver(self):
        return SeleniumTestCase._driver

    def ignore_implicit_wait(self):
        return IgnoreImplicitWait(self.driver, self.selenium_implicit_wait)

    def restore_implicit_wait(self):
        self.driver.implicitly_wait(self.selenium_implicit_wait)

    @classmethod
    def cleanup_browser(cls):
        if cls._driver:
            cls._driver.quit()
            cls._driver = None
