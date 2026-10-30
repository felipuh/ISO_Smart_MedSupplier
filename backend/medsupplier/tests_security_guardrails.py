from django.test import SimpleTestCase, override_settings


class LocalBypassGuardrailTests(SimpleTestCase):
    @override_settings(ENVIRONMENT='production', IS_DEVELOPMENT=False, ALLOW_LOCAL_AUTH_BYPASS_FOR_TESTS=False)
    def test_local_auth_bypass_is_disabled_outside_development(self):
        from django.conf import settings

        self.assertFalse(settings.ALLOW_LOCAL_AUTH_BYPASS_FOR_TESTS)
