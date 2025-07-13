from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url
from allauth.socialaccount.models import SocialAccount

class AccountAdapter(DefaultAccountAdapter):
  def get_signup_redirect_url(self, request):
    user = request.user

    # Check if the user has a social account
    has_social_account = SocialAccount.objects.filter(user=user).exists()
    if has_social_account and not hasattr(user, 'instructor') and not hasattr(user, 'student'):
      return resolve_url('members:select_role')
    return super().get_signup_redirect_url(request)