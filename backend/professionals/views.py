from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from professionals.serializers import ProfessionalSerializer
from professionals.services import DuplicateProfessionalError, create_professional


class ProfessionalView(APIView):
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
