import pytest
from rest_framework import status
from rest_framework.test import APIClient

from professionals.models import Professional


pytestmark = pytest.mark.django_db


def professional_payload(**overrides):
    payload = {
        'full_name': '  Ada Lovelace  ',
        'email': '  ADA@EXAMPLE.COM  ',
        'company_name': '  Analytical Engines Inc  ',
        'job_title': '  Mathematician  ',
        'phone': '+1 (415) 555-0123',
        'source': '  Direct  ',
    }
    payload.update(overrides)
    return payload


@pytest.fixture
def api_client():
    return APIClient()


def test_post_professional_creates_professional(api_client):
    response = api_client.post(
        '/api/professionals/',
        professional_payload(),
        format='json',
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['full_name'] == 'Ada Lovelace'
    assert response.data['email'] == 'ada@example.com'
    assert response.data['phone'] == '+14155550123'
    assert response.data['source'] == Professional.Source.DIRECT
    assert Professional.objects.count() == 1


def test_post_professional_returns_validation_errors(api_client):
    response = api_client.post(
        '/api/professionals/',
        professional_payload(email=' ', phone=' '),
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data['non_field_errors'] == [
        'Either email or phone is required.',
    ]


def test_post_professional_returns_duplicate_errors(api_client):
    Professional.objects.create(
        full_name='Ada Lovelace',
        email='ada@example.com',
        company_name='Analytical Engines Inc',
        job_title='Mathematician',
        phone='+14155550123',
        source=Professional.Source.DIRECT,
    )

    response = api_client.post(
        '/api/professionals/',
        professional_payload(phone='+14155550124'),
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        'email': ['A professional with this email already exists.'],
    }


def _create(**overrides):
    data = {
        'full_name': 'Ada Lovelace',
        'email': 'ada@example.com',
        'company_name': 'Analytical Engines Inc',
        'job_title': 'Mathematician',
        'phone': '+14155550123',
        'source': Professional.Source.DIRECT,
    }
    data.update(overrides)
    return Professional.objects.create(**data)


def test_get_professionals_returns_all(api_client):
    _create(email='ada@example.com', phone='+14155550123', source=Professional.Source.DIRECT)
    _create(email='grace@example.com', phone='+14155550124', source=Professional.Source.PARTNER)

    response = api_client.get('/api/professionals/')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2


def test_get_professionals_filters_by_source(api_client):
    _create(email='ada@example.com', phone='+14155550123', source=Professional.Source.DIRECT)
    _create(email='grace@example.com', phone='+14155550124', source=Professional.Source.PARTNER)
    _create(email='linus@example.com', phone='+14155550125', source=Professional.Source.PARTNER)

    response = api_client.get('/api/professionals/?source=partner')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert {row['email'] for row in response.data} == {'grace@example.com', 'linus@example.com'}


def test_get_professionals_source_filter_is_case_insensitive(api_client):
    _create(email='ada@example.com', phone='+14155550123', source=Professional.Source.INTERNAL)

    response = api_client.get('/api/professionals/?source=INTERNAL')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1


def test_get_professionals_rejects_invalid_source(api_client):
    response = api_client.get('/api/professionals/?source=vip')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'source' in response.data


def test_get_professionals_empty(api_client):
    response = api_client.get('/api/professionals/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []
