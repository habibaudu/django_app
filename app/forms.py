from django import forms
import re
from django.contrib.auth.models import *
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist, ValidationError


class RegistrationForm(forms.ModelForm):

    username =forms.CharField( 
        label='username',required=True,max_length=20,min_length=3)
    email = forms.EmailField( 
        label='email',required=True)
    password =forms.CharField( 
        label='password',required=True,max_length=20,min_length=6,widget = forms.PasswordInput)
    confirm_password= forms.CharField(
        label='confirm_password',required=True,max_length=20,min_length=6,widget = forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = ("username","email","password","confirm_password",)
    
    def clean_confirm_password(self):
        password = self.cleaned_data["password"]
        confirm_password = self.cleaned_data["confirm_password"]
        if password and password != confirm_password:
            raise forms.ValidationError("password don't match")
        return password

    def lowercase_email(email):
        """
        Normalize the address by lowercasing the domain part of the email
        address.
        """
        email = email or ''
        try:
            email_name, domain_part = email.strip().rsplit('@', 1)
        except ValueError:
            pass
        else:
            email = '@'.join([email_name.lower(), domain_part.lower()])
        return email

         
    def clean_email(self):
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError('email already exist')
        return self.cleaned_data['email']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        matche = re.search(r'(\w+)',username)
        if matche is None:
           raise forms.ValidationError('Username must contain only alphanumeric letters and the under_score')
        else:
           return username

class LoginForm(forms.Form):
    username = forms.CharField(label ='Username', max_length=30)
    password = forms.CharField(label='password', widget=forms.PasswordInput())


class BookmarkSaveForm(forms.Form):
    url = forms.URLField( label='URL',
    widget = forms.TextInput(attrs={'size':64}))

    title = forms.CharField(label = 'Title',
    widget = forms.TextInput(attrs={'size':64}))

    tags = forms.CharField(label = 'Tags',
    required = False,
    widget = forms.TextInput(attrs={'size':64}))
    share = forms.BooleanField(label ='Share on The main page', required = False)

class SearchForm(forms.Form):
    query = forms.CharField(
        label = "Enter a keyword to search for",
        widget = forms.TextInput(attrs = {"size":32})
    )

from django.utils.translation import gettext_lazy as _
class FriendInviteForm(forms.Form):
    name = forms.CharField(label=_('Friend\'s Name'))
    email = forms.EmailField(label=_('Friend\'s Email'))