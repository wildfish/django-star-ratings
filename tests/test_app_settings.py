try:
    from importlib import reload
except ImportError:
    from imp import reload
from django.test import TestCase, override_settings
from star_ratings import app_settings


class AppSettingsDefaults(TestCase):
    def tearDown(self):
        reload(app_settings)

    def test_range_not_defined_in_the_settings___defaults_to_five(self):
        reload(app_settings)
        self.assertEqual(5, app_settings.STAR_RATINGS_RANGE)

    @override_settings(STAR_RATINGS_RANGE=10)
    def test_range_defined_in_the_settings___value_is_setting_value(self):
        reload(app_settings)
        self.assertEqual(10, app_settings.STAR_RATINGS_RANGE)
