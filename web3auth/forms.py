import string

from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from web3auth.settings import app_settings
from .utils import validate_xym_address


class LoginForm(forms.Form):
    payload = forms.CharField(widget=forms.HiddenInput, min_length=64)
    # address = forms.CharField(widget=forms.HiddenInput, max_length=42, validators=[validate_eth_address])

    def __init__(self, token, *args, **kwargs):
        self.token = token
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean_signature(self):
        sig = self.cleaned_data['payload']
        if sig == "":
            raise forms.ValidationError(_('Invalid signature'))
        return sig


# list(set()) here is to eliminate the possibility of double including the address field
signup_fields = list(set(app_settings.WEB3AUTH_USER_SIGNUP_FIELDS + [app_settings.WEB3AUTH_USER_ADDRESS_FIELD]))


class SignupForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        # first call parent's constructor
        super().__init__(*args, **kwargs)

        # make sure to make email required, because password is not set
        # and if the user loses private key he can get 'reset' password link to email
        if 'email' in app_settings.WEB3AUTH_USER_SIGNUP_FIELDS:
            self.fields['email'].required = True
        self.fields[app_settings.WEB3AUTH_USER_ADDRESS_FIELD].required = True

    def clean_address_field(self):
        addr = self.cleaned_data[app_settings.WEB3AUTH_USER_ADDRESS_FIELD].replace("-","")
        validate_xym_address(addr)
        return addr

    class Meta:
        model = get_user_model()
        fields = signup_fields


# hack to set the method for cleaning address field
setattr(SignupForm, 'clean_' + app_settings.WEB3AUTH_USER_ADDRESS_FIELD, SignupForm.clean_address_field)
