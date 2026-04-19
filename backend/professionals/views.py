from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from professionals.models import Professional
from professionals.serializers import ProfessionalSerializer
from professionals.services import DuplicateProfessionalError, create_professional


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
