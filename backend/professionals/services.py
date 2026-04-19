from django.db import IntegrityError

from professionals.models import Professional


class DuplicateProfessionalError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__('A professional with this contact information already exists.')


def create_professional(professional_data):
    duplicate_errors = _duplicate_contact_errors(professional_data)

    if duplicate_errors:
        raise DuplicateProfessionalError(duplicate_errors)

    try:
        return Professional.objects.create(**professional_data)
    except IntegrityError as error:
        raise DuplicateProfessionalError({
            'non_field_errors': [
                'A professional with this email or phone already exists.'
            ],
        }) from error


def _duplicate_contact_errors(professional_data):
    errors = {}
    email = professional_data.get('email')
    phone = professional_data.get('phone')

    if email and Professional.objects.filter(email=email).exists():
        errors['email'] = ['A professional with this email already exists.']

    if phone and Professional.objects.filter(phone=phone).exists():
        errors['phone'] = ['A professional with this phone already exists.']

    return errors
