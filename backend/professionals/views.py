from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from professionals.models import Professional
from professionals.serializers import ProfessionalSerializer
from professionals.services import (
    AmbiguousMatchError,
    DuplicateProfessionalError,
    create_professional,
    upsert_professional,
)


class ProfessionalPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProfessionalView(APIView):
    pagination_class = ProfessionalPagination

    def get(self, request):
        queryset = Professional.objects.all()

        source = request.query_params.get('source')
        if source is not None:
            source = source.strip().lower()
            if source not in Professional.Source.values:
                return Response(
                    {'source': [f'"{source}" is not a valid source.']},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            queryset = queryset.filter(source=source)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)
        serializer = ProfessionalSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ProfessionalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            professional = create_professional(serializer.validated_data)
        except DuplicateProfessionalError as error:
            return Response(error.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            ProfessionalSerializer(professional).data,
            status=status.HTTP_201_CREATED,
        )


class ProfessionalBulkView(APIView):
    MAX_BATCH_SIZE = 100

    def post(self, request):
        records = request.data.get('records')

        if not isinstance(records, list) or not records:
            return Response(
                {'records': ['Must be a non-empty list.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(records) > self.MAX_BATCH_SIZE:
            return Response(
                {'records': [
                    f'Cannot exceed {self.MAX_BATCH_SIZE} records per batch.'
                ]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = [self._process_row(index, raw) for index, raw in enumerate(records)]
        summary = self._summarize(results)

        return Response({'summary': summary, 'results': results})

    def _process_row(self, index, raw):
        serializer = ProfessionalSerializer(data=raw if isinstance(raw, dict) else {})

        if not serializer.is_valid():
            return {
                'index': index,
                'status': 'failed',
                'errors': serializer.errors,
            }

        try:
            professional, row_status, enriched_fields = upsert_professional(
                serializer.validated_data
            )
        except AmbiguousMatchError as error:
            return {
                'index': index,
                'status': 'failed',
                'errors': error.errors,
            }

        result = {
            'index': index,
            'status': row_status,
            'professional': ProfessionalSerializer(professional).data,
        }

        if row_status == 'updated':
            result['enriched_fields'] = enriched_fields

        return result

    def _summarize(self, results):
        summary = {'created': 0, 'updated': 0, 'failed': 0, 'total': len(results)}
        for row in results:
            summary[row['status']] += 1
        return summary
