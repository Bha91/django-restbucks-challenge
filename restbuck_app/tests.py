from django.test import TestCase
from restbuck_app.models import *


class FeatureModelTest(TestCase):
    def setUpTestData(cls):
        """ set up test object used by test class. """

        Feature.objects.create(title='thermal_condition')

    def test_title_max_length(self):
        feature = Feature.objects.get(id=1)
        max_length = feature._meta.get_field('title').max_lenght
        self.assertEqual(max_length, 255)

    def test_str_is_feature_title(self):
        feature = Feature.objects.get(id=1)
        expected_str = feature.title
        self.assertEqual(expected_str, str(feature))


class FeaturesValueModelTest(TestCase):
    def setUpTestData(cls):
        feature = Feature.objects.get(id=1)
        FeaturesValue.objects.create(feature=feature, title='cold')
        FeaturesValue.objects.create(feature=feature, title='hot')

    def test_str_is_feature_title_arrow_title(self):
        feature_value = FeaturesValue.objects.get(id=1)
        expected_str = feature_value.feature.title + '-->' + feature_value.title
        self.assertEqual(expected_str, str(feature_value))

    def test_title_max_length(self):
        feature_value = FeaturesValue.objects.get(id=1)
        max_length = feature_value._meta.get_field('title').max_lenght
        self.assertEqual(max_length, 255)


class ProductTest(TestCase):
    def setUpTestData(cls):
        feature = Feature.objects.get(id=1)
        Product.objects.create(title='Water', feature=feature, cost=2)

    def test_title_max_length(self):
        product = Product.objects.get(id=1)
        max_length = product._meta.get_field('title').max_lenght
        self.assertEqual(max_length, 255)

    def test_str_is_product_title(self):
        product = Product.objects.get(id=1)
        expected_str = product.title
        self.assertEqual(expected_str, str(product))


class OrderTest(TestCase):
    def setUpTestData(cls):
        user = User.objects.create_user(username='testuser1', password='Drc#1234')
        Order.objects.create(user=user)

    def test_is_deleted_label(self):
        order = Order.objects.get(id=1)
        field_label = order._meta.get_field('is_deleted').verbose_name
        self.assertEqual(field_label, 'is deleted')


