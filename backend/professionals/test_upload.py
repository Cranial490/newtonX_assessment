import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient


UPLOAD_URL = '/api/professionals/upload/csv/'

HEADER = 'full_name,email,company_name,job_title,phone,source\n'


def csv_file(content, name='records.csv'):
    return SimpleUploadedFile(name, content.encode('utf-8'), content_type='text/csv')


@pytest.fixture
def api_client():
    return APIClient()


def test_upload_returns_normalized_valid_rows(api_client):
    body = HEADER + (
        '  Ada Lovelace ,  ADA@EXAMPLE.COM ,Analytical Engines Inc,Mathematician,+1 (415) 555-0123,  Direct  \n'
        'Grace Hopper,grace@example.com,Navy,Rear Admiral,+14155550124,partner\n'
    )

    response = api_client.post(UPLOAD_URL, {'file': csv_file(body)}, format='multipart')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['summary'] == {'valid': 2, 'failed': 0, 'total': 2}
    first = response.data['records'][0]['record']
    assert response.data['records'][0]['index'] == 0
    assert response.data['records'][0]['status'] == 'valid'
    assert first['full_name'] == 'Ada Lovelace'
    assert first['email'] == 'ada@example.com'
    assert first['phone'] == '+14155550123'
    assert first['source'] == 'direct'


def test_upload_returns_valid_and_failed_rows(api_client):
    body = HEADER + (
        'Ada Lovelace,ada@example.com,Analytical Engines Inc,Mathematician,+14155550123,direct\n'
        'Bad Source,bad@example.com,Co,Title,+14155550124,vip\n'
        'No Contact,,Co,Title,,direct\n'
    )

    response = api_client.post(UPLOAD_URL, {'file': csv_file(body)}, format='multipart')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['summary'] == {'valid': 1, 'failed': 2, 'total': 3}
    assert len(response.data['records']) == 3
    assert response.data['records'][0]['status'] == 'valid'
    assert response.data['records'][0]['record']['email'] == 'ada@example.com'
    assert response.data['records'][1]['status'] == 'failed'
    assert response.data['records'][1]['record']['source'] == 'vip'
    assert 'source' in response.data['records'][1]['errors']
    assert response.data['records'][2]['status'] == 'failed'
    assert 'non_field_errors' in response.data['records'][2]['errors']


def test_upload_rejects_missing_file(api_client):
    response = api_client.post(UPLOAD_URL, {}, format='multipart')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'file' in response.data


def test_upload_rejects_empty_csv(api_client):
    response = api_client.post(UPLOAD_URL, {'file': csv_file('')}, format='multipart')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'file' in response.data


def test_upload_rejects_header_only_csv(api_client):
    response = api_client.post(UPLOAD_URL, {'file': csv_file(HEADER)}, format='multipart')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'file' in response.data


def test_upload_rejects_oversized_csv(api_client):
    rows = ''.join(
        f'User {i},user{i}@example.com,Co,Title,+1415555{i:04d},direct\n'
        for i in range(101)
    )
    body = HEADER + rows

    response = api_client.post(UPLOAD_URL, {'file': csv_file(body)}, format='multipart')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'file' in response.data


def test_upload_rejects_non_utf8(api_client):
    raw = HEADER.encode('utf-8') + b'Ada,\xff\xfe,Co,Title,+14155550123,direct\n'
    upload = SimpleUploadedFile('records.csv', raw, content_type='text/csv')

    response = api_client.post(UPLOAD_URL, {'file': upload}, format='multipart')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'file' in response.data
