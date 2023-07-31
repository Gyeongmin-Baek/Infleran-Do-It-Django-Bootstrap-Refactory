from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.http import HttpResponseRedirect
from django.views.generic import View


class GoogleLoginView(View):
    def get(self, request):
        social_app = SocialApp.objects.filter(provider="google").first()
        callback_url = GoogleOAuth2Adapter(request).get_callback_url(
            request, social_app
        )
        client = OAuth2Client(
            request,
            social_app.client_id,
            social_app.secret,
            social_app.token_method,
            social_app.token_url,
            callback_url,
            social_app.scope,
        )
        authorize_url = client.get_redirect_url()
        return HttpResponseRedirect(authorize_url)
