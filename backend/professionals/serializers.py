from collections.abc import Mapping
import re

from rest_framework import serializers

from professionals.models import Professional


PHONE_ALLOWED_PATTERN = re.compile(r'^\+?[0-9\s().-]+$')
PHONE_MIN_DIGITS = 7
PHONE_MAX_DIGITS = 15


class StrictCharField(serializers.CharField):
    def to_internal_value(self, data):
        if not isinstance(data, str):
            self.fail('invalid')

        return super().to_internal_value(data)


class StrictEmailField(serializers.EmailField):
    def to_internal_value(self, data):
        if not isinstance(data, str):
            self.fail('invalid')

        return super().to_internal_value(data)


class ProfessionalSerializer(serializers.ModelSerializer):
    full_name = StrictCharField(max_length=255)
    email = StrictEmailField(
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    company_name = StrictCharField(
        max_length=255,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    job_title = StrictCharField(
        max_length=255,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    phone = StrictCharField(
        allow_blank=True,
        allow_null=True,
        max_length=32,
        required=False,
    )
    source = StrictCharField(max_length=16)

    class Meta:
        model = Professional
        fields = [
            'id',
            'full_name',
            'email',
            'company_name',
            'job_title',
            'phone',
            'source',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def to_internal_value(self, data):
        if isinstance(data, Mapping):
            data = self._drop_unknown_fields(data)

        return super().to_internal_value(data)

    def validate_source(self, value):
        normalized_source = value.strip().lower()
        valid_sources = Professional.Source.values

        if normalized_source not in valid_sources:
            raise serializers.ValidationError(
                f'Invalid source. Expected one of: {", ".join(valid_sources)}.'
            )

        return normalized_source

    def validate(self, attrs):
        attrs = super().validate(attrs)

        self._validate_contact_identity(attrs)
        attrs = self._normalize(attrs)

        return attrs

    def _drop_unknown_fields(self, data):
        writable_fields = {
            field.field_name
            for field in self._writable_fields
        }

        return {
            field_name: value
            for field_name, value in data.items()
            if field_name in writable_fields
        }

    def _validate_contact_identity(self, attrs):
        email = attrs.get('email')
        phone = attrs.get('phone')

        if not self._has_value(email) and not self._has_value(phone):
            raise serializers.ValidationError(
                'Either email or phone is required.'
            )

    def _normalize(self, attrs):
        normalized_attrs = attrs.copy()

        normalized_attrs['full_name'] = normalized_attrs['full_name'].strip()
        normalized_attrs['source'] = normalized_attrs['source'].strip().lower()

        for field_name in ['company_name', 'job_title']:
            if field_name in normalized_attrs:
                normalized_attrs[field_name] = self._normalize_optional_string(
                    normalized_attrs[field_name]
                )

        normalized_attrs['email'] = self._normalize_email(
            normalized_attrs.get('email')
        )
        normalized_attrs['phone'] = self._normalize_phone(
            normalized_attrs.get('phone')
        )

        return normalized_attrs

    def _normalize_email(self, value):
        normalized_value = self._normalize_optional_string(value)

        if normalized_value is None:
            return None

        return normalized_value.lower()

    def _normalize_optional_string(self, value):
        if value is None:
            return None

        normalized_value = value.strip()

        if not normalized_value:
            return None

        return normalized_value

    def _normalize_phone(self, value):
        normalized_value = self._normalize_optional_string(value)

        if normalized_value is None:
            return None

        if not PHONE_ALLOWED_PATTERN.fullmatch(normalized_value):
            raise serializers.ValidationError({
                'phone': 'Enter a valid phone number.'
            })

        has_plus = normalized_value.startswith('+')
        digits = re.sub(r'\D', '', normalized_value)

        if not PHONE_MIN_DIGITS <= len(digits) <= PHONE_MAX_DIGITS:
            raise serializers.ValidationError({
                'phone': 'Enter a valid phone number.'
            })

        if has_plus:
            return f'+{digits}'

        return digits

    def _has_value(self, value):
        if value is None:
            return False

        return bool(value.strip())
