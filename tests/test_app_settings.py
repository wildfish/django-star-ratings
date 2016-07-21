from django.test import TestCase, override_settings
from star_ratings import app_settings


class AppSettingsDefaults(TestCase):
    def test_range_not_defined_in_the_settings___defaults_to_five(self):
        self.assertEqual(5, app_settings.STAR_RATINGS_RANGE)

    @override_settings(STAR_RATINGS_RANGE=10)
    def test_range_defined_in_the_settings___value_is_setting_value(self):
        self.assertEqual(10, app_settings.STAR_RATINGS_RANGE)

    def test_rerate_not_defined_in_the_settings___defaults_to_true(self):
        self.assertTrue(app_settings.STAR_RATINGS_RERATE)

    @override_settings(STAR_RATINGS_RERATE=False)
    def test_rerate_defined_in_the_settings___value_is_setting_value(self):
        self.assertFalse(app_settings.STAR_RATINGS_RERATE)

    def test_anon_ratings_not_defined_in_settings___defaults_to_false(self):
        self.assertFalse(app_settings.STAR_RATINGS_ANONYMOUS)

    @override_settings(STAR_RATINGS_ANONYMOUS=True)
    def test_anon_ratings_defined_in_the_settings___value_is_setting_value(self):
        self.assertTrue(app_settings.STAR_RATINGS_ANONYMOUS)
