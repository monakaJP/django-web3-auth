from django.contrib.auth import get_user_model, backends
from django.conf import settings

from web3auth.settings import app_settings
from web3auth.utils import recover_to_addr
from web3auth.utils import publicKey_to_addr


class Web3Backend(backends.ModelBackend):
    def authenticate(self, request, token=None, signature=None):
        # get user model
        User = get_user_model()
        # check if the address the user has provided matches the signature
        if not recover_to_addr(token, signature):
            return None
        else:
            print("validate success")
            # get address field for the user model
            address_field = app_settings.WEB3AUTH_USER_ADDRESS_FIELD
            kwargs = {
                f"{address_field}__iexact": publicKey_to_addr(signature[:64],settings.NETWORK_TYPE)
            }
            # try to get user with provided data
            user = User.objects.filter(**kwargs).first()
            return user
