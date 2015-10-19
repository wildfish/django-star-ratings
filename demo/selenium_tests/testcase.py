from django.contrib.staticfiles.testing import StaticLiveServerTestCase
import os
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
    """
    Metaclass for the selenium test case. This handles creating the extra test cases when using remote drivers so
    that multiple driver types can be used. When remote drives are not being used we fall back to Firefox
    """
    def __new__(meta, classname, bases, class_dict):
        sauce_url = "http://%s:%s@ondemand.saucelabs.com:80/wd/hub" % (_sauce_username, _sauce_access_key)

        new_class_dict = {}

        # Add each attribute to the new class.
        for attr_name, attr_value in class_dict.items():
            if callable(attr_value) and attr_name.startswith('test_'):
                # If the attribute is a test we wrap it passing a driver to it
                method = attr_value

                if _use_remote_driver:
                    # If we are using remote browsers loop over each specified browser and wrap the test in its driver
                    for browser in _remote_browsers:
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
                    # If we are not using remote drivers wrap each test with the firefox driver
                    driver_fn = webdriver.Firefox
                    method_name = '{orig_name}___firefox'.format(orig_name=attr_name)
                    new_class_dict[method_name] = meta._new_method(method, driver_fn)

            else:
                # If the attribute is not a test we do not modify it
                new_class_dict[attr_name] = attr_value

        return type.__new__(meta, classname, bases, new_class_dict)

    @classmethod
    def _new_method(cls, method, driver_fn):
        """
        Method for wrapping the test cases with the driver. The driver is created, the test is ran, then the driver is
        destroyed.

        :param method: The test method to be wrapped
        :param driver_fn: Function to generate the driver
        """
        def _new(self):
            driver = driver_fn()
            try:
                method(self, driver)
            finally:
                driver.quit()

        return _new


class SeleniumTestCase(with_metaclass(SeleniumTestCaseMeta, StaticLiveServerTestCase)):
    """
    Class to handle creating a test server and creating test cases for each driver
    """
    pass
