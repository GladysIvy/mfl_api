import django_filters

from django import forms
from django.utils.encoding import force_str
from django.utils.dateparse import parse_datetime
from rest_framework import ISO_8601


class IsoDateTimeField(forms.DateTimeField):
    """
    It support 'iso-8601' date format too which is out the scope of
    the ``datetime.strptime`` standard library

    # ISO 8601: ``http://www.w3.org/TR/NOTE-datetime``
    """
    def strptime(self, value, format):
        value = force_str(value)
        if format == ISO_8601:
            parsed = parse_datetime(value)
            if parsed is None:  # Continue with other formats if doesn't match
                raise ValueError
            return parsed
        return super(IsoDateTimeField, self).strptime(value, format)


class IsoDateTimeFilter(django_filters.DateTimeFilter):
    """ Extend ``DateTimeFilter`` to filter by ISO 8601 formated dates too"""
    field_class = IsoDateTimeField


class CommonFieldsFilterset(django_filters.FilterSet):
    """Every model that descends from AbstractBase should have this

    The usage pattern for this is presently simplistic; mix it in, then add to
    the `fields` in the filter's `Meta` `'updated', 'created',
    updated_before', 'created_before', 'updated_after', 'created_after'' and
    any other applicable / extra fields.

    When you inherit this, DO NOT add a `fields` declaration. Let the implicit
    filter fields ( every model field gets one ) stay in place.
    """
    updated_before = IsoDateTimeFilter(
        name='updated', lookup_type='lte',
        input_formats=(ISO_8601, '%m/%d/%Y %H:%M:%S'))
    created_before = IsoDateTimeFilter(
        name='created', lookup_type='lte',
        input_formats=(ISO_8601, '%m/%d/%Y %H:%M:%S'))

    updated_after = IsoDateTimeFilter(
        name='updated', lookup_type='gte',
        input_formats=(ISO_8601, '%m/%d/%Y %H:%M:%S'))
    created_after = IsoDateTimeFilter(
        name='created', lookup_type='gte',
        input_formats=(ISO_8601, '%m/%d/%Y %H:%M:%S'))

    updated_on = IsoDateTimeFilter(
        name='updated', lookup_type='exact',
        input_formats=(ISO_8601, '%m/%d/%Y %H:%M:%S'))
    created_on = IsoDateTimeFilter(
        name='created', lookup_type='exact',
        input_formats=(ISO_8601, '%m/%d/%Y %H:%M:%S'))

    is_deleted = django_filters.BooleanFilter(
        name='deleted', lookup_type='exact')
    is_active = django_filters.BooleanFilter(
        name='active', lookup_type='exact')
