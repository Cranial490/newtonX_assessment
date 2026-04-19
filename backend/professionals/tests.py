from django.apps import apps

from professionals.models import Professional


def test_professionals_app_is_installed():
    app_config = apps.get_app_config('professionals')

    assert app_config.name == 'professionals'


def test_professional_source_choices_match_assignment():
    assert Professional.Source.values == ['direct', 'partner', 'internal']


def test_professional_string_representation_uses_full_name():
    professional = Professional(full_name='Ada Lovelace')

    assert str(professional) == 'Ada Lovelace'


def test_professional_default_ordering_is_deterministic():
    assert Professional._meta.ordering == ['-created_at', 'id']
