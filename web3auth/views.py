import json

from django.conf import settings
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.shortcuts import render, redirect, reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods

from web3auth.forms import LoginForm, SignupForm
from web3auth.settings import app_settings


def get_redirect_url(request):
    if request.GET.get('next'):
        return request.GET.get('next')
    elif request.POST.get('next'):
        return request.POST.get('next')
    elif settings.LOGIN_REDIRECT_URL:
        try:
            url = reverse(settings.LOGIN_REDIRECT_URL)
        except NoReverseMatch:
            url = settings.LOGIN_REDIRECT_URL
        return url


@require_http_methods(["GET", "POST"])
def login_api(request):
    if request.method == 'GET':
        token = settings.PUB
        request.session['login_token'] = token
        return JsonResponse({'data': token, 'success': True})
    else:
        print("auth...")
        token = request.session.get('login_token')
        print("token",token)
        print("form:",request.POST)
        if not token:
            return JsonResponse({'error': _(
                "No login token in session, please request token again by sending GET request to this url"),
                'success': False})
        else:
            form = LoginForm(token, request.POST)
            if form.is_valid():
                payload = form.cleaned_data.get("payload")
                # signature, address = form.cleaned_data.get("payload"), form.cleaned_data.get("address")
                print("payload:",payload)
                del request.session['login_token']
                try:
                    user = authenticate(request, token=token, signature=payload)
                    print(user)
                    if user:
                        login(request, user, 'web3auth.backend.Web3Backend')

                        return JsonResponse({'success': True, 'redirect_url': get_redirect_url(request)})
                    else:
                        error = _("Can't find a user for the provided signature with address {address}").format(
                            address=payload[:64])
                        return JsonResponse({'success': False, 'error': error})
                except ValueError(e):
                    print(e)
                    return JsonResponse({'success': False, 'error': "invalid value"})
            else:
                print("form error")
                return JsonResponse({'success': False, 'error': json.loads(form.errors.as_json())})


@require_http_methods(["POST"])
def signup_api(request):
    if not app_settings.WEB3AUTH_SIGNUP_ENABLED:
        return JsonResponse({'success': False, 'error': _("Sorry, signup's are currently disabled")})
    form = SignupForm(request.POST)
    if form.is_valid():
        user = form.save(commit=False)
        addr_field = app_settings.WEB3AUTH_USER_ADDRESS_FIELD
        setattr(user, addr_field, form.cleaned_data[addr_field])
        user.save()
        login(request, user, 'web3auth.backend.Web3Backend')
        return JsonResponse({'success': True, 'redirect_url': get_redirect_url(request)})
    else:
        return JsonResponse({'success': False, 'error': json.loads(form.errors.as_json())})


@require_http_methods(["GET", "POST"])
def signup_view(request, template_name='web3auth/signup.html'):
    """
    1. Creates an instance of a SignupForm.
    2. Checks if the registration is enabled.
    3. If the registration is closed or form has errors, returns form with errors
    4. If the form is valid, saves the user without saving to DB
    5. Sets the user address from the form, saves it to DB
    6. Logins the user using web3auth.backend.Web3Backend
    7. Redirects the user to LOGIN_REDIRECT_URL or 'next' in get or post params
    :param request: Django request
    :param template_name: Template to render
    :return: rendered template with form
    """
    form = SignupForm()
    if not app_settings.WEB3AUTH_SIGNUP_ENABLED:
        form.add_error(None, _("Sorry, signup's are currently disabled"))
    else:
        if request.method == 'POST':
            form = SignupForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                addr_field = app_settings.WEB3AUTH_USER_ADDRESS_FIELD
                setattr(user, addr_field, form.cleaned_data[addr_field])
                user.save()
                login(request, user, 'web3auth.backend.Web3Backend')
                return redirect(get_redirect_url(request))
    return render(request,
                  template_name,
                  {'form': form})
