from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend

class EmailAuthBackend(ModelBackend):
    """
    Email Authentication Backend

    Allows a user to sign in using an email/password or username/password pair
    """

    def authenticate(self, username=None, password=None):
        """
        Authenticate a user based on email address or username
        """
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            try:
                user = User.objects.get(username=username)
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                return None
