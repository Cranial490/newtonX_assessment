import pytest
from rest_framework import status
from rest_framework.test import APIClient

from professionals.models import Professional


pytestmark = pytest.mark.django_db

BULK_URL = '/api/professionals/bulk/'


def record(**overrides):
    data = {
        'full_name': 'Ada Lovelace',
        'email': 'ada@example.com',
        'company_name': 'Analytical Engines Inc',
        'job_title': 'Mathematician',
        'phone': '+14155550123',
        'source': 'direct',
    }
    data.update(overrides)
    return data


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


@pytest.fixture
def api_client():
    return APIClient()


def test_bulk_creates_new_records(api_client):
    payload = {'records': [
        record(email='ada@example.com', phone='+14155550123'),
        record(email='grace@example.com', phone='+14155550124'),
    ]}

    response = api_client.post(BULK_URL, payload, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['summary'] == {'created': 2, 'updated': 0, 'failed': 0, 'total': 2}
    assert Professional.objects.count() == 2
    for row in response.data['results']:
        assert row['status'] == 'created'
        assert 'enriched_fields' not in row


def test_bulk_enriches_missing_fields_only(api_client):
    existing = _create(
        email='ada@example.com',
        phone=None,
        job_title='',
    )

    payload = {'records': [record(
        full_name='Augusta King',
        email='ada@example.com',
        phone='+14155550124',
        job_title='Countess',
    )]}

    response = api_client.post(BULK_URL, payload, format='json')

    existing.refresh_from_db()
    assert response.status_code == status.HTTP_200_OK
    row = response.data['results'][0]
    assert row['status'] == 'updated'
    assert set(row['enriched_fields']) == {'phone', 'job_title'}
    assert existing.full_name == 'Ada Lovelace'
    assert existing.phone == '+14155550124'
    assert existing.job_title == 'Countess'
    assert response.data['summary']['updated'] == 1


def test_bulk_does_not_overwrite_existing_phone(api_client):
    existing = _create(email='ada@example.com', phone='+14155550123')

    payload = {'records': [record(
        email='ada@example.com',
        phone='+14155559999',
    )]}

    response = api_client.post(BULK_URL, payload, format='json')

    existing.refresh_from_db()
    row = response.data['results'][0]
    assert row['status'] == 'updated'
    assert row['enriched_fields'] == []
    assert existing.phone == '+14155550123'


def test_bulk_reports_validation_errors_per_row(api_client):
    payload = {'records': [
        record(email='ada@example.com', phone='+14155550123'),
        record(email='bad@example.com', phone='+14155550124', source='vip'),
    ]}

    response = api_client.post(BULK_URL, payload, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['summary'] == {'created': 1, 'updated': 0, 'failed': 1, 'total': 2}
    assert response.data['results'][0]['status'] == 'created'
    assert response.data['results'][1]['status'] == 'failed'
    assert 'source' in response.data['results'][1]['errors']
    assert Professional.objects.count() == 1


def test_bulk_flags_ambiguous_match(api_client):
    _create(email='ada@example.com', phone='+14155550123')
    _create(email='grace@example.com', phone='+14155550124')

    payload = {'records': [record(
        email='ada@example.com',
        phone='+14155550124',
    )]}

    response = api_client.post(BULK_URL, payload, format='json')

    row = response.data['results'][0]
    assert row['status'] == 'failed'
    assert row['errors'] == {
        'non_field_errors': ['Matches multiple existing professionals.'],
    }


def test_bulk_rejects_missing_records_key(api_client):
    response = api_client.post(BULK_URL, {}, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'records' in response.data


def test_bulk_rejects_empty_records_list(api_client):
    response = api_client.post(BULK_URL, {'records': []}, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'records' in response.data


def test_bulk_rejects_oversized_batch(api_client):
    payload = {'records': [
        record(email=f'user{i}@example.com', phone=f'+1415555{i:04d}')
        for i in range(101)
    ]}

    response = api_client.post(BULK_URL, payload, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'records' in response.data
    assert Professional.objects.count() == 0


def test_bulk_sequential_duplicates_within_payload(api_client):
    payload = {'records': [
        record(email='ada@example.com', phone=None),
        record(email='ada@example.com', phone='+14155550124'),
    ]}

    response = api_client.post(BULK_URL, payload, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['summary'] == {'created': 1, 'updated': 1, 'failed': 0, 'total': 2}
    assert response.data['results'][0]['status'] == 'created'
    assert response.data['results'][1]['status'] == 'updated'
    assert response.data['results'][1]['enriched_fields'] == ['phone']
    assert Professional.objects.count() == 1
