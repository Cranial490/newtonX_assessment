import pytest

from professionals.models import Professional
from professionals.services import (
    AmbiguousMatchError,
    DuplicateProfessionalError,
    create_professional,
    upsert_professional,
)


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


def test_upsert_professional_creates_when_no_match():
    professional, status, enriched_fields = upsert_professional(professional_data())

    assert status == 'created'
    assert enriched_fields == []
    assert professional.id is not None
    assert Professional.objects.count() == 1


def test_upsert_professional_enriches_only_empty_fields():
    existing = Professional.objects.create(**professional_data(
        phone=None,
        job_title='',
    ))

    professional, status, enriched_fields = upsert_professional(professional_data(
        full_name='Augusta King',
        phone='+14155550124',
        job_title='Countess',
    ))

    existing.refresh_from_db()
    assert status == 'updated'
    assert professional.pk == existing.pk
    assert set(enriched_fields) == {'phone', 'job_title'}
    assert existing.full_name == 'Ada Lovelace'
    assert existing.phone == '+14155550124'
    assert existing.job_title == 'Countess'


def test_upsert_professional_reports_empty_enriched_fields_when_nothing_changes():
    Professional.objects.create(**professional_data())

    _, status, enriched_fields = upsert_professional(professional_data(
        full_name='Augusta King',
    ))

    assert status == 'updated'
    assert enriched_fields == []


def test_upsert_professional_raises_on_ambiguous_match():
    Professional.objects.create(**professional_data(
        email='ada@example.com',
        phone='+14155550123',
    ))
    Professional.objects.create(**professional_data(
        email='grace@example.com',
        phone='+14155550124',
    ))

    with pytest.raises(AmbiguousMatchError) as error:
        upsert_professional(professional_data(
            email='ada@example.com',
            phone='+14155550124',
        ))

    assert error.value.errors == {
        'non_field_errors': ['Matches multiple existing professionals.'],
    }
