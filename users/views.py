from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .models import CustomUser, Pledge, Project  # Import Project model
from .serializers import CustomUserSerializer, PledgeSerializer, ProjectSerializer  # Import ProjectSerializer

# CustomUser List (GET and POST requests)
class CustomUserList(APIView):
   def get(self, request):
       users = CustomUser.objects.all()
       serializer = CustomUserSerializer(users, many=True)
       return Response(serializer.data)

   def post(self, request):
       serializer = CustomUserSerializer(data=request.data)
       if serializer.is_valid():
           serializer.save()
           return Response(
               serializer.data,
               status=status.HTTP_201_CREATED
           )
       return Response(
           serializer.errors, 
           status=status.HTTP_400_BAD_REQUEST
       )

# CustomUser Detail (GET request)
class CustomUserDetail(APIView):
   def get_object(self, pk):
       try:
           return CustomUser.objects.get(pk=pk)
       except CustomUser.DoesNotExist:
           raise Http404

   def get(self, request, pk):
       user = self.get_object(pk)
       serializer = CustomUserSerializer(user)
       return Response(serializer.data)

# Custom Auth Token (POST request)
class CustomAuthToken(ObtainAuthToken):
   def post(self, request, *args, **kwargs):
       serializer = self.serializer_class(
           data=request.data,
           context={'request': request}
       )
       serializer.is_valid(raise_exception=True)
       user = serializer.validated_data['user']
       token, created = Token.objects.get_or_create(user=user)

       return Response({
           'token': token.key,
           'user_id': user.id,
           'email': user.email
       })

# Create Pledge (POST request)
class CreatePledge(APIView):
    def post(self, request):
        # Serialize the incoming data
        serializer = PledgeSerializer(data=request.data)

        if serializer.is_valid():
            # Save the pledge to the database
            serializer.save()

            # Return a success response with a status of 201 (Created)
            return Response({"success": True, "message": "Pledge created!"}, status=status.HTTP_201_CREATED)
        
        # Return the errors if data is invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# List Projects (GET request)
class ProjectList(APIView):
    def get(self, request):
        projects = Project.objects.all()  # Get all projects from the database
        serializer = ProjectSerializer(projects, many=True)  # Serialize the list of projects
        return Response(serializer.data)  # Return the serialized data

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)  # Serialize incoming project data
        if serializer.is_valid():
            serializer.save()  # Save the new project to the database
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )



