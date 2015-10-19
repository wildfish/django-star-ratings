from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import os
import sys
from selenium import webdriver
from six import with_metaclass

_sauce_username = os.environ.get('SAUCE_USERNAME', None)
_sauce_access_key = os.environ.get('SAUCE_ACCESS_KEY', None)
_travis_job_number = os.environ.get('TRAVIS_JOB_NUMBER', None)
_use_remote_driver = _travis_job_number is not None

_remote_browsers = [
    {
        'platform': 'Linux',
        'browserName': 'chrome',
        'version': '',
        'tunnelIdentifier': _travis_job_number,
    },
    {
        'platform': 'Linux',
        'browserName': 'firefox',
        'version': '',
        'tunnelIdentifier': _travis_job_number,
    },
    {
        'platform': 'Linux',
        'browserName': 'opera',
        'version': '',
        'tunnelIdentifier': _travis_job_number,
    },
    #
    # disabled while ms work on the driver
    #
    # {
    #     'platform': 'Windows 10',
    #     'browserName': 'microsoftedge',
    #     'version': '',
    #     'tunnelIdentifier': _travis_job_number,
    # },
    #
    # disabled while ms work on the driver
    #
    {
        'platform': 'Windows 10',
        'browserName': 'internet explorer',
        'version': '11',
        'tunnelIdentifier': _travis_job_number,
    },
    {
        'platform': 'Windows 8',
        'browserName': 'internet explorer',
        'version': '10',
        'tunnelIdentifier': _travis_job_number,
    },
    {
        'platform': 'Windows 7',
        'browserName': 'internet explorer',
        'version': '9',
        'tunnelIdentifier': _travis_job_number,
    },
    {
        'platform': 'Mac OS X 10.11',
        'browserName': 'safari',
        'version': '',
        'tunnelIdentifier': _travis_job_number,
    },
    {
        'platform': 'Linux',
        'browserName': 'android',
        'deviceName': "Android Emulator",
        'version': "5.1",
        'tunnelIdentifier': _travis_job_number,
    },
    {
        'platform': 'Linux',
        'browserName': 'android',
        'deviceName': "Android Emulator",
        'version': "5.0",
        'tunnelIdentifier': _travis_job_number,
    },
    {
        'platform': 'Linux',
        'browserName': 'android',
        'deviceName': "Android Emulator",
        'version': "4.4",
        'tunnelIdentifier': _travis_job_number,
    },
    {
        'platform': 'Linux',
        'browserName': 'android',
        'deviceName': "Android Emulator",
        'version': "4.3",
        'tunnelIdentifier': _travis_job_number,
    },
    {
        'platform': 'Linux',
        'browserName': 'android',
        'deviceName': "Android Emulator",
        'version': "4.2",
        'tunnelIdentifier': _travis_job_number,
    },
    {
        'platform': 'Linux',
        'browserName': 'android',
        'deviceName': "Android Emulator",
        'version': "4.1",
        'tunnelIdentifier': _travis_job_number,
    },
    {
        'platform': 'OS X 10.10',
        'browserName': 'iPhone',
        'deviceName': 'iPhone Simulator',
        'version': '',
        'tunnelIdentifier': _travis_job_number,
    },
    {
        'platform': 'OS X 10.10',
        'browserName': 'iPhone',
        'deviceName': 'iPhone Simulator',
        'version': '8.4',
        'tunnelIdentifier': _travis_job_number,
    },
    {
        'platform': 'OS X 10.10',
        'browserName': 'iPhone',
        'deviceName': 'iPad Simulator',
        'version': '',
        'tunnelIdentifier': _travis_job_number,
    },
    {
        'platform': 'OS X 10.10',
        'browserName': 'iPhone',
        'deviceName': 'iPad Simulator',
        'version': '8.4',
        'tunnelIdentifier': _travis_job_number,
    }
]


class RemoteDriverWrapper(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        return webdriver.Remote(*self.args, **self.kwargs)


class SeleniumTestCaseMeta(type):
    def __new__(meta, classname, bases, class_dict):
        new_class_dict = {}

        for attr_name, attr_value in class_dict.items():
            if callable(attr_value) and attr_name.startswith('test_'):
                method = attr_value

                if _use_remote_driver:
                    sauce_url = "http://%s:%s@ondemand.saucelabs.com:80/wd/hub" % (_sauce_username, _sauce_access_key)
                    for i, browser in enumerate(_remote_browsers):
                        print(browser)

                        driver_fn = RemoteDriverWrapper(
                            desired_capabilities=browser,
                            command_executor=sauce_url
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

        print(new_class_dict)

        return type.__new__(meta, classname, bases, new_class_dict)

    @classmethod
    def _new_method(cls, method, driver_fn):
        def _new(self):
            print('Creating driver')
            driver = driver_fn()
            try:
                print('running test', driver)
                method(self, driver)
                print('test ran')
            finally:
                print('closing driver', driver)
                driver.quit()

        return _new


class SeleniumTestCase(with_metaclass(SeleniumTestCaseMeta, StaticLiveServerTestCase)):
    pass
