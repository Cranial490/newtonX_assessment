import pytest

from professionals.models import Professional
from professionals.services import DuplicateProfessionalError, create_professional


pytestmark = pytest.mark.django_db


def professional_data(**overrides):
    data = {
        'full_name': 'Ada Lovelace',
        'email': 'ada@example.com',
        'company_name': 'Analytical Engines Inc',
        'job_title': 'Mathematician',
        'phone': '+14155550123',
        'source': Professional.Source.DIRECT,
    }
    data.update(overrides)
    return data


def test_create_professional_persists_validated_data():
    professional = create_professional(professional_data())

    assert professional.id is not None
    assert professional.email == 'ada@example.com'
    assert Professional.objects.count() == 1


def test_create_professional_rejects_duplicate_email():
    Professional.objects.create(**professional_data())

    with pytest.raises(DuplicateProfessionalError) as error:
        create_professional(professional_data(phone='+14155550124'))

    assert error.value.errors == {
        'email': ['A professional with this email already exists.'],
    }


def test_create_professional_rejects_duplicate_phone():
    Professional.objects.create(**professional_data())

    with pytest.raises(DuplicateProfessionalError) as error:
        create_professional(professional_data(
            email='grace@example.com',
            phone='+14155550123',
        ))

    assert error.value.errors == {
        'phone': ['A professional with this phone already exists.'],
    }
