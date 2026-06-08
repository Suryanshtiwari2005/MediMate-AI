import os
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
import requests

User = get_user_model()


@api_view(['GET'])
@permission_classes([AllowAny])
def google_login(request):
    """
    Feature #1: Google OAuth 2.0 Login
    Returns the Google OAuth2 authorization URL for the frontend to redirect to.
    """
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:8000/auth/callback/')
    scope = 'openid email profile'
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope={scope}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return Response({'auth_url': auth_url})


@api_view(['GET'])
@permission_classes([AllowAny])
def google_callback(request):
    """
    Feature #2: JWT Session Management + Feature #14: Avatar from Google
    Exchanges Google authorization code for tokens, creates/gets User,
    saves avatar from Google profile, and issues JWT tokens.
    """
    code = request.GET.get('code')
    if not code:
        return Response({'error': 'No authorization code provided'}, status=400)

    # Exchange code for Google tokens
    token_resp = requests.post('https://oauth2.googleapis.com/token', data={
        'code': code,
        'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
        'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
        'redirect_uri': os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:8000/auth/callback/'),
        'grant_type': 'authorization_code',
    })
    token_data = token_resp.json()

    if 'error' in token_data:
        return Response({'error': token_data['error']}, status=400)

    # Get user info from Google
    userinfo_resp = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f"Bearer {token_data['access_token']}"}
    )
    userinfo = userinfo_resp.json()

    # Create or get user — Feature #14: avatar_url saved from Google profile
    user, created = User.objects.get_or_create(
        google_id=userinfo['id'],
        defaults={
            'username': userinfo['email'].split('@')[0],
            'email': userinfo['email'],
            'full_name': userinfo.get('name', ''),
            'avatar_url': userinfo.get('picture', ''),
        }
    )
    if not created:
        # Update profile info on each login
        user.full_name = userinfo.get('name', user.full_name)
        user.avatar_url = userinfo.get('picture', user.avatar_url)
        user.save()

    # Issue JWT tokens — Feature #2
    refresh = RefreshToken.for_user(user)
    refresh['role'] = user.role
    refresh['email'] = user.email

    # Redirect to frontend with tokens in URL params
    frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
    redirect_url = (
        f"{frontend_url}/login"
        f"?access={str(refresh.access_token)}"
        f"&refresh={str(refresh)}"
        f"&user_id={user.id}"
        f"&role={user.role}"
        f"&name={user.full_name}"
        f"&avatar={user.avatar_url or ''}"
    )
    return redirect(redirect_url)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auth_me(request):
    """Return current authenticated user's info."""
    user = request.user
    return Response({
        'id': user.id,
        'email': user.email,
        'full_name': user.full_name,
        'role': user.role,
        'avatar_url': user.avatar_url,
        'whatsapp_number': user.whatsapp_number,
        'has_profile': hasattr(user, 'patient_profile'),
        'onboarding_done': getattr(user, 'patient_profile', None) and user.patient_profile.onboarding_done or False,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auth_logout(request):
    """
    Feature #6: Secure Logout
    Blacklists the refresh token so it can't be reused.
    Frontend should also clear its local state.
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
    except Exception:
        pass  # Token may already be invalid/expired — that's fine
    return Response({'success': True})
