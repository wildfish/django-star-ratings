from copy import copy
from unittest import TextTestResult, TestSuite
from unittest.runner import _WritelnDecorator
from django.test.runner import DiscoverRunner
import os
from selenium import webdriver
import sys

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


class SeleniumTestRunner(DiscoverRunner):
    def _drivers(self):
        if _use_remote_driver:
            sauce_url = "http://%s:%s@ondemand.saucelabs.com:80/wd/hub" % (_sauce_username, _sauce_access_key)
            # If we are using remote browsers loop over each specified browser and wrap the test in its driver
            for browser in _remote_browsers:
                browser_tag = '{}_{}_{}'.format(
                    browser['platform'],
                    browser['browserName'],
                    browser['version'] or 'latest',
                ).replace(' ', '_')

                yield browser_tag, webdriver.Remote(
                    desired_capabilities=browser,
                    command_executor=sauce_url
                )
        else:
            # If we are not using remote drivers wrap each test with the firefox driver
            yield 'firefox', webdriver.Firefox()

    def run_suite(self, suite, **kwargs):
        orig_tests = list(suite._tests)

        result = TextTestResult(_WritelnDecorator(sys.stderr), True, self.verbosity)
        for tag, driver in self._drivers():
            try:
                tests = []

                # Modify each test so that the description tells us which browser we are using
                for t in orig_tests:
                    new_test = copy(t)
                    new_test.driver = driver
                    new_test._testMethodDoc = 'Ran on "{}"'.format(tag)
                    tests.append(new_test)

                TestSuite(tests).run(result)
            finally:
                driver.quit()

                # This resets the previous class in the results so that the setupClass will be ran for the next driver
                setattr(result, '_previousTestClass', None)

        result.printErrors()
        return result
