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
    assert response.data['count'] == 2
    assert len(response.data['results']) == 2


def test_get_professionals_filters_by_source(api_client):
    _create(email='ada@example.com', phone='+14155550123', source=Professional.Source.DIRECT)
    _create(email='grace@example.com', phone='+14155550124', source=Professional.Source.PARTNER)
    _create(email='linus@example.com', phone='+14155550125', source=Professional.Source.PARTNER)

    response = api_client.get('/api/professionals/?source=partner')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 2
    assert {row['email'] for row in response.data['results']} == {'grace@example.com', 'linus@example.com'}


def test_get_professionals_source_filter_is_case_insensitive(api_client):
    _create(email='ada@example.com', phone='+14155550123', source=Professional.Source.INTERNAL)

    response = api_client.get('/api/professionals/?source=INTERNAL')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1


def test_get_professionals_rejects_invalid_source(api_client):
    response = api_client.get('/api/professionals/?source=vip')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'source' in response.data


def test_get_professionals_empty(api_client):
    response = api_client.get('/api/professionals/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 0
    assert response.data['results'] == []


def test_get_professional_stats_empty(api_client):
    response = api_client.get('/api/professionals/stats/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        'total': 0,
        'complete': 0,
        'source_counts': {
            'direct': 0,
            'partner': 0,
            'internal': 0,
        },
    }


def test_get_professional_stats(api_client):
    _create(
        email='complete@example.com',
        phone='+14155550123',
        company_name='Analytical Engines Inc',
        job_title='Mathematician',
        source=Professional.Source.DIRECT,
    )
    _create(
        email='missing-company@example.com',
        phone='+14155550124',
        company_name=None,
        job_title='Rear Admiral',
        source=Professional.Source.PARTNER,
    )
    _create(
        email=None,
        phone='+14155550125',
        company_name='Bell Labs',
        job_title='',
        source=Professional.Source.PARTNER,
    )

    response = api_client.get('/api/professionals/stats/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        'total': 3,
        'complete': 1,
        'source_counts': {
            'direct': 1,
            'partner': 2,
            'internal': 0,
        },
    }


def test_get_professionals_paginates(api_client):
    for i in range(25):
        _create(
            email=f'user{i}@example.com',
            phone=f'+1415555{i:04d}',
            source=Professional.Source.DIRECT,
        )

    first = api_client.get('/api/professionals/')
    assert first.status_code == status.HTTP_200_OK
    assert first.data['count'] == 25
    assert len(first.data['results']) == 20
    assert first.data['next'] is not None
    assert first.data['previous'] is None

    second = api_client.get('/api/professionals/?page=2')
    assert second.status_code == status.HTTP_200_OK
    assert len(second.data['results']) == 5
    assert second.data['next'] is None
    assert second.data['previous'] is not None


def test_get_professionals_respects_page_size_override(api_client):
    for i in range(5):
        _create(
            email=f'user{i}@example.com',
            phone=f'+1415555{i:04d}',
            source=Professional.Source.DIRECT,
        )

    response = api_client.get('/api/professionals/?page_size=2')

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 2
    assert response.data['count'] == 5
