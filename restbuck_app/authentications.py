""" Customized authentication classes for restbuck_app application. """
from rest_framework import authentication


class BearerAuthentication(authentication.TokenAuthentication):
    keyword = 'Bearer'

