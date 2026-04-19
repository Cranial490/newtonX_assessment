import pytest

from professionals.models import Professional
from professionals.serializers import ProfessionalSerializer


pytestmark = pytest.mark.django_db


def professional_payload(**overrides):
    payload = {
        'full_name': 'Ada Lovelace',
        'email': 'ada@example.com',
        'company_name': 'Analytical Engines Inc',
        'job_title': 'Mathematician',
        'phone': '+14155550123',
        'source': Professional.Source.DIRECT,
    }
    payload.update(overrides)
    return payload


def assert_serializer_errors(payload, field_name):
    serializer = ProfessionalSerializer(data=payload)

    assert not serializer.is_valid()
    assert field_name in serializer.errors


def test_professional_serializer_normalizes_valid_payload():
    serializer = ProfessionalSerializer(data=professional_payload(
        full_name='  Ada Lovelace  ',
        email='  ADA@EXAMPLE.COM  ',
        company_name='  Analytical Engines Inc  ',
        job_title='  Mathematician  ',
        phone='  +14155550123  ',
        source='  Direct  ',
    ))

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data == {
        'full_name': 'Ada Lovelace',
        'email': 'ada@example.com',
        'company_name': 'Analytical Engines Inc',
        'job_title': 'Mathematician',
        'phone': '+14155550123',
        'source': Professional.Source.DIRECT,
    }


def test_professional_serializer_converts_blank_optional_contact_fields_to_none():
    serializer = ProfessionalSerializer(data=professional_payload(
        email=' ',
        phone='+14155550123',
    ))

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data['email'] is None
    assert serializer.validated_data['phone'] == '+14155550123'


@pytest.mark.parametrize(
    ('phone', 'normalized_phone'),
    [
        ('+1 (415) 555-0123', '+14155550123'),
        ('415 555 0123', '4155550123'),
        ('415.555.0123', '4155550123'),
    ],
)
def test_professional_serializer_normalizes_common_phone_formats(
    phone,
    normalized_phone,
):
    serializer = ProfessionalSerializer(data=professional_payload(phone=phone))

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data['phone'] == normalized_phone


def test_professional_serializer_requires_email_or_phone():
    serializer = ProfessionalSerializer(data=professional_payload(
        email=' ',
        phone=None,
    ))

    assert not serializer.is_valid()
    assert serializer.errors['non_field_errors'] == [
        'Either email or phone is required.'
    ]


def test_professional_serializer_rejects_null_non_nullable_fields():
    assert_serializer_errors(
        professional_payload(full_name=None),
        'full_name',
    )


def test_professional_serializer_rejects_non_string_values():
    assert_serializer_errors(
        professional_payload(full_name=123),
        'full_name',
    )


def test_professional_serializer_rejects_invalid_email_string():
    assert_serializer_errors(
        professional_payload(email='not-an-email'),
        'email',
    )


@pytest.mark.parametrize(
    'phone',
    [
        'not-a-phone',
        '555-CALL-NOW',
        '@@@',
        '123',
    ],
)
def test_professional_serializer_rejects_invalid_phone_strings(phone):
    assert_serializer_errors(
        professional_payload(phone=phone),
        'phone',
    )


def test_professional_serializer_rejects_invalid_source():
    assert_serializer_errors(
        professional_payload(source='external'),
        'source',
    )


def test_professional_serializer_silently_drops_unknown_fields():
    serializer = ProfessionalSerializer(data=professional_payload(
        source_metadata={'campaign': 'spring'},
    ))

    assert serializer.is_valid(), serializer.errors
    assert 'source_metadata' not in serializer.validated_data


def test_professional_serializer_allows_duplicate_email_for_upsert_flow():
    Professional.objects.create(**professional_payload())

    serializer = ProfessionalSerializer(data=professional_payload(
        email='ADA@example.com',
        phone='+14155550124',
    ))

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data['email'] == 'ada@example.com'


def test_professional_serializer_allows_duplicate_phone_for_upsert_flow():
    Professional.objects.create(**professional_payload())

    serializer = ProfessionalSerializer(data=professional_payload(
        email='grace@example.com',
        phone='+1 (415) 555-0123',
    ))

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data['phone'] == '+14155550123'
