from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import Http404
from .models import Project, Pledge
from .serializers import ProjectSerializer, PledgeSerializer, ProjectDetailSerializer, PledgeDetailSerializer
from .permissions import IsOwnerOrReadOnly, IsSupporterOrReadOnly


class ProjectList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        # use the project model to get a list of all projects in the db
        projects = Project.objects.all()
        # use the project serializer to convert that list to JSON
        serializer = ProjectSerializer(projects, many=True)
        #return a response containing the serialized data
        return Response(serializer.data)
    
    def post(self, request):
        print(f"Request Data: {request.data}")
        print(f"Request Files: {request.FILES}")

        # Handle file upload
        file = request.FILES.get('image')
        image_url = None
        if file:
            # Upload the file to S3
            image_url = upload_to_s3(file)
            if image_url:
                request.data['image'] = image_url  # Include the image URL in the request data
            else:
                return Response({"error": "Failed to upload image to S3"}, status=status.HTTP_400_BAD_REQUEST)
       
        serializer = ProjectSerializer(data=request.data)
        print(f"Final request data: {request.data}")

        if serializer.is_valid():
            serializer.save(owner=request.user)
            print("Project created successfully!")

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        print(f"Serializer Errors: {serializer.errors}")
        return Response(
            serializer.errors,
            status=status.HTTP_401_UNAUTHORIZED
        )

class ProjectDetail(APIView):

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly
    ]

    def get_object(self, pk):
        try:
            project = Project.objects.get(pk=pk)
            self.check_object_permissions(self.request, project)
            return project
        except Project.DoesNotExist:
            raise Http404
        
    def get(self, request, pk):
        project = self.get_object(pk)
        serializer = ProjectDetailSerializer(project)
        return Response(serializer.data)
    
    def put(self, request, pk):
        project = self.get_object(pk)
        serializer = ProjectDetailSerializer(
            instance=project,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def delete(self, request, pk):
        project = self.get_object(pk)
        project.delete()
        return Response(
            {"message": "Project deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )

class PledgeList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        pledges = Pledge.objects.all()
        serializer = PledgeSerializer(pledges, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = PledgeSerializer(data=request.data)
        print(request.data)
        print(request.user)
        try:
            if serializer.is_valid():
                serializer.save(supporter=request.user)
                return Response(
                    serializer.data, 
                    status=status.HTTP_201_CREATED
                )
            else:
                print(serializer.errors)
        except e as Exception:
            print(e)
            return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

        return Response(
            serializer.errors,
            status=status.HTTP_401_UNAUTHORIZED
        )

class PledgeDetail(APIView):

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsSupporterOrReadOnly
    ]

    def get_object(self, pk):
        try:
            pledge = Pledge.objects.get(pk=pk)
            self.check_object_permissions(self.request, pledge)
            return pledge
        except Pledge.DoesNotExist:
            raise Http404
        
    def get(self, request, pk):
        pledge = self.get_object(pk)
        serializer = PledgeDetailSerializer(pledge)
        return Response(serializer.data)
    
    def put(self, request, pk):
        pledge = self.get_object(pk)
        serializer = PledgeDetailSerializer(
            instance=pledge,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    def delete(self, request, pk):
        pledge = self.get_object(pk)
        pledge.delete()
        return Response(
            {"message": "Pledge deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )