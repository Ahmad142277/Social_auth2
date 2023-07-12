import json

from requests_oauthlib import OAuth2Session
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
import requests
from google.oauth2 import id_token
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
from django.views.decorators.csrf import csrf_exempt


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

client_secrets_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "g_client_secret.json")

flow = Flow.from_client_secrets_file(
     client_secrets_file=client_secrets_file,
     scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
     redirect_uri="http://127.0.0.1:8000/google/callback"
   )

GOOGLE_CLIENT_ID = "750007652305-5hgjrsifqmevqn3r22p7kti0e3m5a6fd.apps.googleusercontent.com"

class GoogleLoginAPIView(APIView):
    @csrf_exempt
    def get(self, request):

        authorization_url, state = flow.authorization_url()
        request.session["state"] = state

        return Response({"authorization_url": authorization_url}, status=status.HTTP_200_OK)

class GoogleCallbackAPIView(APIView):
    @csrf_exempt
    def get(self, request):
        flow.fetch_token(authorization_response=request.build_absolute_uri())

        if not request.session["state"] == request.GET["state"]:
            return Response({"message": "Invalid state parameter"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        credentials = flow.credentials
        request_session = requests.session()
        cached_session = cachecontrol.CacheControl(request_session)
        token_request = google.auth.transport.requests.Request(session=cached_session)

        id_info = id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=token_request,
            audience=GOOGLE_CLIENT_ID
        )
        access_token = credentials.token
        url = 'http://127.0.0.1:8000/api-auth/convert-token'

        # Request payload (data to be sent)
        payload = {
            "grant_type": "convert_token",
            "client_id": "rQX034EgS8e9kODDyg9y0BMqISBOn5lsyW9hJp9u",
            "client_secret": "SFfKV6zwZSxrpvnRNWF14fquAPlGQmGyAgEXQzKduuvbUa2I7r2DD8zncG1In51redW8lNWnffvW0y05lkaASw9QyKTsUGOYreC4PFkgoQ4jlUENBHAThTn1eyCC04YE",
            "backend": "google-oauth2",
            "token": access_token
        }

        # Convert payload to JSON
        json_payload = json.dumps(payload)

        # Set the appropriate headers for JSON data
        headers = {
            'Content-Type': 'application/json'
        }

        # Send the POST request with JSON data
        response = requests.post(url, data=json_payload, headers=headers)

        # Check the response status code
        if response.status_code == 200:
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


FACEBOOK_CLIENT_ID = "407987610634920"
FACEBOOK_CLIENT_SECRET = "7723f1b576be6935f43c80287a80c22c"
REDIRECT_URI = "https://127.0.0.1:8000/callback"

authorization_base_url = "https://www.facebook.com/v14.0/dialog/oauth"
token_url = "https://graph.facebook.com/v14.0/oauth/access_token"
scope = ["email"]

class facebookLoginAPIView(APIView):
    @csrf_exempt
    def get(self, request):
        facebook = OAuth2Session(
            client_id=FACEBOOK_CLIENT_ID,
            redirect_uri=REDIRECT_URI,
            scope=scope,
        )
        authorization_url, state = facebook.authorization_url(authorization_base_url)
        request.session["state"] = state
        return Response({"authorization_url": authorization_url}, status=status.HTTP_200_OK)

class facebookCallbackAPIView(APIView):
    @csrf_exempt
    def get(self, request):
        if "error" in request.GET:
            return Response({"message": "Invalid state parameter"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not request.session["state"] == request.GET["state"]:
            return Response({"message": "Invalid state parameter"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        facebook = OAuth2Session(
            client_id=FACEBOOK_CLIENT_ID,
            redirect_uri=REDIRECT_URI,
            scope=scope,
        )

        token_response = facebook.fetch_token(
            token_url,
            client_secret=FACEBOOK_CLIENT_SECRET,
            authorization_response=request.build_absolute_uri(),
        )

        access_tokenfb = token_response["access_token"]
        url = 'http://127.0.0.1:8000/api-auth/convert-token'

        # Request payload (data to be sent)
        payload = {
            "grant_type": "convert_token",
            "client_id": "rQX034EgS8e9kODDyg9y0BMqISBOn5lsyW9hJp9u",
            "client_secret": "SFfKV6zwZSxrpvnRNWF14fquAPlGQmGyAgEXQzKduuvbUa2I7r2DD8zncG1In51redW8lNWnffvW0y05lkaASw9QyKTsUGOYreC4PFkgoQ4jlUENBHAThTn1eyCC04YE",
            "backend": "facebook",
            "token": access_tokenfb
        }

        # Convert payload to JSON
        json_payload = json.dumps(payload)

        # Set the appropriate headers for JSON data
        headers = {
            'Content-Type': 'application/json'
        }

        # Send the POST request with JSON data
        response = requests.post(url, data=json_payload, headers=headers)

        # Check the response status code
        if response.status_code == 200:
            return Response(response, status=status.HTTP_200_OK)
        else:
            return Response(response, status=status.HTTP_400_BAD_REQUEST)