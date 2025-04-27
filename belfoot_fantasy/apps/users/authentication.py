import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

def custom_authenticate(request):
    #ModelAuth
    #response = JWTAuthentication().authenticate(request)

    #GoogleOAuth2.0
    authenticate_url = 'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=ya29.a0AZYkNZhcC50bBTKEVTYxyILjpC14QMnVa0NsH3cjgakvIgYnaPWVCHCZmTuiXmzPwfEXF_14mXchj1cJn_LDarnXncUk1ZrS4uZbcws2IzXFsjPFd8M5P7k3BN_wn094b3moSwKWWLe_G4OEmJO_3doDb7dzmvyKe_EYjSgLaCgYKAfoSARcSFQHGX2MixOljRKSV3f01yv335Z1EfA0175'

    response = requests.post(authenticate_url)

    if response.status_code == 200:
        return True

    else:
        return Response(status=status.HTTP_403_FORBIDDEN)




