from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from Users.serializers import UserSerializer, PersonSerializer

class LoginView(APIView):
    authentication_classes = [] # Allow unauthenticated access
    permission_classes = []

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        print(f"DEBUG: Login attempt for email: {email}") # DEBUG
        
        if not email or not password:
            return Response({'detail': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)

        # Custom auth backend or standard ModelBackend if username=email
        # Since CustomUser uses email as USERNAME_FIELD, authenticate should work if passed as username or handled by backend
        user = authenticate(request, username=email, password=password)
        
        print(f"DEBUG: Authenticate result: {user}") # DEBUG

        if user is not None:
            if not user.is_active:
                return Response({'detail': 'Account is disabled'}, status=status.HTTP_403_FORBIDDEN)
            
            login(request, user) # Sets the session cookie
            
            # Serialize User + Person
            user_data = UserSerializer(user).data
            if hasattr(user, 'person'):
                user_data['person'] = PersonSerializer(user.person).data
            
            return Response(user_data, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'detail': 'Logged out successfully'}, status=status.HTTP_200_OK)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_data = UserSerializer(user).data
        if hasattr(user, 'person'):
                user_data['person'] = PersonSerializer(user.person).data
        return Response(user_data)
