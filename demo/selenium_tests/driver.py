from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import os
import sys
from selenium import webdriver

_sauce_username = os.environ.get('SAUCE_USERNAME', '')
_sauce_access_key = os.environ.get('SAUCE_ACCESS_KEY', '')
_travis_job_number = os.environ.get('TRAVIS_JOB_NUMBER', None)
_use_remote_driver = _travis_job_number is not None

_remote_browsers = [
    {
        'platform': 'Mac OS X 10.9',
        'browserName': 'chrome',
        'version': '31',
        'tunnelIdentifier': _travis_job_number,
    },
    {
        'platform': 'Windows 8.1',
        'browserName': 'internet explorer',
        'version': '11',
        'tunnelIdentifier': _travis_job_number,
    }
]


class SeleniumTestCaseMeta(type):
    def __new__(meta, classname, bases, class_dict):
        new_class_dict = {}

        for attr_name, attr_value in class_dict.items():
            if callable(attr_value) and attr_name.startswith('test_'):
                method = attr_value

                if _use_remote_driver:
                    sauce_url = "http://%s:%s@ondemand.saucelabs.com:80/wd/hub".format(_sauce_username, _sauce_access_key)
                    for i, browser in enumerate(_remote_browsers):
                        driver_fn = lambda: webdriver.Remote(
                            desired_capabilities=browser,
                            command_executor=sauce_url % (_sauce_username, _sauce_access_key)
                        )

                        browser_tag = '{}_{}_{}'.format(
                            browser['platform'],
                            browser['browserName'],
                            browser['version']
                        ).replace(' ', '_')

                        method_name = '{orig_name}___{tag}'.format(orig_name=attr_name, tag=browser_tag)
                        new_class_dict[method_name] = meta._new_method(method, driver_fn)

                else:
                    driver_fn = webdriver.Chrome
                    method_name = '{orig_name}___firefox'.format(orig_name=attr_name)
                    new_class_dict[method_name] = meta._new_method(method, driver_fn)

            else:
                new_class_dict[attr_name] = attr_value

        return type.__new__(meta, classname, bases, new_class_dict)

    @classmethod
    def _new_method(cls, method, driver_fn):
        def _new(self):
            driver = driver_fn()
            try:
                method(self, driver)
            finally:
                driver.quit()

        return _new


class SeleniumTestCase(StaticLiveServerTestCase, metaclass=SeleniumTestCaseMeta):
    pass
