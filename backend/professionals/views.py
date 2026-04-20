import csv
import io

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
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


class ProfessionalCsvUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    MAX_ROWS = 100

    def post(self, request):
        upload = request.FILES.get('file')

        if upload is None:
            return Response(
                {'file': ['No file uploaded.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            text = upload.read().decode('utf-8-sig')
        except UnicodeDecodeError:
            return Response(
                {'file': ['File must be UTF-8 encoded.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reader = csv.DictReader(io.StringIO(text))

        if reader.fieldnames is None:
            return Response(
                {'file': ['CSV is empty or missing a header row.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw_rows = [
            {key: (value.strip() if isinstance(value, str) else value)
             for key, value in row.items() if key is not None}
            for row in reader
        ]

        if not raw_rows:
            return Response(
                {'file': ['CSV has no data rows.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(raw_rows) > self.MAX_ROWS:
            return Response(
                {'file': [f'Cannot exceed {self.MAX_ROWS} rows per upload.']},
                status=status.HTTP_400_BAD_REQUEST,
            )

        records = []
        for index, row in enumerate(raw_rows):
            serializer = ProfessionalSerializer(data=row)
            if serializer.is_valid():
                records.append({
                    'index': index,
                    'status': 'valid',
                    'record': serializer.validated_data,
                })
            else:
                records.append({
                    'index': index,
                    'status': 'failed',
                    'record': row,
                    'errors': serializer.errors,
                })

        summary = self._summarize(records)

        return Response({
            'summary': summary,
            'records': records,
        })

    def _summarize(self, records):
        summary = {'valid': 0, 'failed': 0, 'total': len(records)}
        for row in records:
            summary[row['status']] += 1
        return summary
