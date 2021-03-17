from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from restbuck_app.serializers import *
from restbuck_app.models import *

client = APIClient()


class FeatureModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        """ set up test object used by test class. """

        Feature.objects.create(title='thermal_condition')

    def test_title_max_length(self):
        feature = Feature.objects.get(id=1)
        max_length = feature._meta.get_field('title').max_length
        self.assertEqual(max_length, 255)

    def test_str_is_feature_title(self):
        feature = Feature.objects.get(id=1)
        expected_str = feature.title
        self.assertEqual(expected_str, str(feature))


class FeaturesValueModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        feature = Feature.objects.create(title='thermal_condition')
        FeaturesValue.objects.create(feature=feature, title='cold')
        FeaturesValue.objects.create(feature=feature, title='hot')

    def test_str_is_feature_title_arrow_title(self):
        feature_value = FeaturesValue.objects.get(id=1)
        expected_str = feature_value.feature.title + '-->' + feature_value.title
        self.assertEqual(expected_str, str(feature_value))

    def test_title_max_length(self):
        feature_value = FeaturesValue.objects.get(id=1)
        max_length = feature_value._meta.get_field('title').max_length
        self.assertEqual(max_length, 255)


class ProductTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        feature = Feature.objects.create(title='thermal_condition')
        Product.objects.create(title='Water', feature=feature, cost=2)

    def test_title_max_length(self):
        product = Product.objects.get(id=1)
        max_length = product._meta.get_field('title').max_length
        self.assertEqual(max_length, 255)

    def test_str_is_product_title(self):
        product = Product.objects.get(id=1)
        expected_str = product.title
        self.assertEqual(expected_str, str(product))


class OrderTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user(username='testuser1', password='Drc#1234')
        Order.objects.create(user=user)

    def test_is_deleted_label(self):
        order = Order.objects.get(id=1)
        field_label = order._meta.get_field('is_deleted').verbose_name
        self.assertEqual(field_label, 'is deleted')


class MenuViewTest(TestCase):
    def setUp(self) -> None:
        size_feature = Feature.objects.create(title='size')
        thermal_feature = Feature.objects.create(title='thermal')
        FeaturesValue.objects.create(title='small', feature=size_feature)
        FeaturesValue.objects.create(title='big', feature=size_feature)
        FeaturesValue.objects.create(title='cold', feature=thermal_feature)
        FeaturesValue.objects.create(title='hot', feature=thermal_feature)
        Product.objects.create(title='water', cost='2', feature=size_feature)
        Product.objects.create(title='milk', cost='4', feature=thermal_feature)
        user = User.objects.create(username='test1', password='Ronash#1234')
        token = Token.objects.create(user=user)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_get_menu_ok(self):
        response = client.get(reverse('get_menu'))
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        self.assertEqual(response.data.get('data'), serializer.data)
        self.assertFalse(response.data.get('error'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_menu_not_authenticated(self):
        client.logout()
        response = client.get(reverse('get_menu'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderViewTest(TestCase):
    def setUp(self) -> None:
        size_feature = Feature.objects.create(title='size')
        thermal_feature = Feature.objects.create(title='thermal')
        FeaturesValue.objects.create(title='small', feature=size_feature)
        FeaturesValue.objects.create(title='big', feature=size_feature)
        FeaturesValue.objects.create(title='cold', feature=thermal_feature)
        FeaturesValue.objects.create(title='hot', feature=thermal_feature)
        Product.objects.create(title='water', cost='2', feature=size_feature)
        Product.objects.create(title='milk', cost='4', feature=thermal_feature)
        user = User.objects.create(username='test1', password='Ronash#1234')
        token = Token.objects.create(user=user)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)


