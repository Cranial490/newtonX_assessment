from django.apps import apps


def test_professionals_app_is_installed():
    app_config = apps.get_app_config('professionals')

    assert app_config.name == 'professionals'
