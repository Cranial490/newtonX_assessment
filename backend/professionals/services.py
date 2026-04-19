from django.db import IntegrityError

from professionals.models import Professional


ENRICHABLE_FIELDS = [
    'full_name',
    'email',
    'company_name',
    'job_title',
    'phone',
    'source',
]


class DuplicateProfessionalError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__('A professional with this contact information already exists.')


class AmbiguousMatchError(Exception):
    def __init__(self):
        self.errors = {
            'non_field_errors': ['Matches multiple existing professionals.'],
        }
        super().__init__(self.errors['non_field_errors'][0])


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


def upsert_professional(professional_data):
    existing = _find_match(professional_data)

    if existing is None:
        professional = Professional.objects.create(**professional_data)
        return professional, 'created', []

    enriched_fields = _enrich(existing, professional_data)
    return existing, 'updated', enriched_fields


def _duplicate_contact_errors(professional_data):
    errors = {}
    email = professional_data.get('email')
    phone = professional_data.get('phone')

    if email and Professional.objects.filter(email=email).exists():
        errors['email'] = ['A professional with this email already exists.']

    if phone and Professional.objects.filter(phone=phone).exists():
        errors['phone'] = ['A professional with this phone already exists.']

    return errors


def _find_match(professional_data):
    email = professional_data.get('email')
    phone = professional_data.get('phone')

    email_match = (
        Professional.objects.filter(email=email).first() if email else None
    )
    phone_match = (
        Professional.objects.filter(phone=phone).first() if phone else None
    )

    if email_match and phone_match and email_match.pk != phone_match.pk:
        raise AmbiguousMatchError()

    return email_match or phone_match


def _enrich(existing, incoming):
    enriched_fields = []

    for field_name in ENRICHABLE_FIELDS:
        incoming_value = incoming.get(field_name)

        if not _has_value(incoming_value):
            continue

        current_value = getattr(existing, field_name)

        if _has_value(current_value):
            continue

        setattr(existing, field_name, incoming_value)
        enriched_fields.append(field_name)

    if enriched_fields:
        existing.save(update_fields=enriched_fields)

    return enriched_fields


def _has_value(value):
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True
