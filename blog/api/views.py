import ipdb
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie,vary_on_headers
from rest_framework.decorators import api_view,permission_classes,action
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter,OrderingFilter 
from .models import Blog
from .serializers import BlogSerializer,UserSerializer
from rest_framework.permissions import BasePermission,IsAuthenticated, AllowAny, IsAdminUser,SAFE_METHODS
from django.core.exceptions import PermissionDenied

# Using APIview for FBV
'''
@api_view(['GET',"POST"])
@permission_classes([IsAuthenticated])
def BlogList(request):
     blog=Blog.objects.all()
     serializer=BlogSerializer(blog,many=True)
     createSerializer=BlogSerializer(data=request.data)
     if request.method=="GET":
        return Response(serializer.data)
     elif request.method=="POST":
          if createSerializer.is_valid():
            createSerializer.save(author=request.user)
            return Response(createSerializer.data)
'''       
# Using Viewset
'''
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

'''


class UserRate(UserRateThrottle):
     rate="10/day"

# authorize or not 
class ReadOnly(BasePermission):
     def has_permission(self, request, view):
          return request.method in SAFE_METHODS
     
# check author's permissions
class IsOwnerOrReadOnly(BasePermission):
     def has_object_permission(self, request, view, obj):
          if request.method in SAFE_METHODS:
               return True
          return obj.author ==  request.user


class BlogList(generics.ListCreateAPIView):
        serializer_class=BlogSerializer
        permission_classes=[IsAuthenticated | ReadOnly]
        # throttle_classes=[UserRate]
        lookup_field="pk"
        lookup_url_kwarg='blog-list'

        # http://127.0.0.1:8000/api/notes/?search=spi&?ordering=date&page=1

        pagination_class=PageNumberPagination # why? 
        filter_backends=[SearchFilter,OrderingFilter]
        search_fields=['title','date']
        ordering_fields=['date','title']
        ordering=['date']

        @method_decorator(cache_page(60 * 60 * 2))
        @method_decorator(vary_on_cookie)
        @method_decorator(vary_on_headers("Authorization"))
        def get(self, request, *args, **kwargs):
             return super().get(request, *args, **kwargs)
        def get_queryset(self):
            # ipdb.set_trace()
            return Blog.objects.select_related("author").all()
        
        @action(detail=False, methods=['POST'])
        def perform_create(self,serializer):
            # ipdb.set_trace()
            serializer=serializer.save(author=self.request.user)
            # send_email_confirmation(user=self.request.user, modified=serializer)


        # Not need to memorize
        # Not to be overridden 
        '''def filter_queryset(self, queryset):
            filter_backends = [CategoryFilter]

            if 'geo_route' in self.request.query_params:
                filter_backends = [GeoRouteFilter, CategoryFilter]
            elif 'geo_point' in self.request.query_params:
                filter_backends = [GeoPointFilter, CategoryFilter]

            for backend in list(filter_backends):
                queryset = backend().filter_queryset(self.request, queryset, view=self)

            return queryset'''

class DeleteBlog(generics.DestroyAPIView):
    queryset = Blog.objects.all()
    serializer_class=BlogSerializer
    permission_classes=[IsAuthenticated & IsOwnerOrReadOnly]

    '''def get_object(self):
        blog=super().get_object()
        if blog.author !=self.request.user:
                raise PermissionDenied("You do not have permission to delete this blog.")
        return blog'''
    
class UpdateBlog(generics.UpdateAPIView):
    queryset = Blog.objects.all()
    serializer_class=BlogSerializer
    # applying IsOwnerOrReadOnly
    permission_classes=[IsAuthenticated & IsOwnerOrReadOnly]

    # alternative of IsOwnerOrReadyOnly 
    # Only checks author name does check the whole object of author
    '''def get_object(self):
        ''''''get_object will automatically take pk from url, no need to pass it in func''''''
        blog=super().get_object()
        if blog.author !=self.request.user:
                raise PermissionDenied("You do not have permission to update this blog.")
        return blog'''
    
class CreateUserView(generics.CreateAPIView):
    '''Queryset required'''
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    '''queryset = SignupRequest.objects.filter(user=self.request.user)
        if queryset.exists():
            raise ValidationError('You have already signed up')
        serializer.save(user=self.request.user)'''

class ViewUser(APIView):
     '''NO Queryset required
        Can use multiple methods like POST,PUT,DELETE etc for function
     '''
     serializer_class=UserSerializer
     permission_classes=[IsAdminUser]
     def get(self,request):
          username=[user.username for user in User.objects.all()]
          return Response(username) 
     

     
class LoginUser(APIView):
     permission_classes=[AllowAny]
     def post(self,request):
          username=request.data.get('username')
          password=request.data.get('password')
          user=authenticate(request,password=password,username=username)
          if  not password or not username:
               return Response({"Username and Password required"})
          if user is not None:
               refresh = RefreshToken.for_user(user)
               access_token = str(refresh.access_token)
               return Response({
                "message": "Login successfully",
                "access": access_token,
                "refresh": str(refresh)
            })
          else:
               return Response({"Invalid Ceredentials"})