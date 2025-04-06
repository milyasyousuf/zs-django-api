
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken


def custom_exception_handler(exc, context):
    # Call the default exception handler first
    response = exception_handler(exc, context)

    # Handle InvalidToken and AuthenticationFailed exceptions
    if isinstance(exc, (InvalidToken, AuthenticationFailed, NotAuthenticated)):
        return Response(
            {"detail": "Invalid or expired token."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    return response
