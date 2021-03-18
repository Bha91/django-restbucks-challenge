from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from restbuck_app.serializers import *
from restbuck_app.models import *
from restbuck_app.views import OrderView

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
        user1 = User.objects.create(username='test1', password='Ronash#1234')
        user2 = User.objects.create(username='test2', password='Ronash#1234')
        Order.objects.create(user=user1)
        Order.objects.create(user=user1, state=OrderStatus.preparation)
        Order.objects.create(user=user2)
        token = Token.objects.create(user=user1)
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def test_get_single_order_by_id(self):
        user = User.objects.get(id=1)
        order = Order.objects.filter(user=user).first()
        serializer = OrderSerializer(order)
        response = client.get(reverse('client_order', args=(order.id,)))
        self.assertEqual(response.data.get('data'), serializer.data)
        self.assertFalse(response.data.get('error'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_others_order_403(self):
        user2 = User.objects.get(id=2)
        order = Order.objects.filter(user=user2).first()
        response = client.get(reverse('client_order', args=(order.id,)))
        self.assertTrue(response.data.get('error'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get('message'), 'Not your order')

    def test_get_not_existed_order(self):
        response = client.get(reverse('client_order', args=(1000,)))
        self.assertTrue(response.data.get('error'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get('message'), 'requested order dose not exist')

    def test_get_all_order(self):
        user = User.objects.get(id=1)
        orders = Order.objects.filter(user=user)
        serializer = OrderSerializer(orders, many=True)
        response = client.get(reverse('client_order'))
        self.assertEqual(response.data.get('data'), serializer.data)
        self.assertFalse(response.data.get('error'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_order_not_authenticated(self):
        client.logout()
        response = client.get(reverse('client_order'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_my_waiting_order_by_id(self):
        user = User.objects.get(id=1)
        order = Order.objects.filter(user=user, state=OrderStatus.waiting).first()
        response = client.delete(reverse('client_order', args=(order.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_my_not_waiting_order_by_id(self):
        user = User.objects.get(id=1)
        order = Order.objects.filter(user=user).exclude(state=OrderStatus.waiting).first()
        response = client.delete(reverse('client_order', args=(order.id,)))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('message'), 'Not valid order state')
        self.assertTrue(response.data.get('error'))

    def test_delete_others_order_403(self):
        user2 = User.objects.get(id=2)
        order = Order.objects.filter(user=user2).first()
        response = client.delete(reverse('client_order', args=(order.id,)))
        self.assertTrue(response.data.get('error'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data.get('message'), 'Not your order')

    def test_delete_not_existed_order(self):
        response = client.get(reverse('client_order', args=(1000,)))
        self.assertTrue(response.data.get('error'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data.get('message'), 'requested order dose not exist')

    # TODO: get, deleted orders already deleted before

    def test_post_new_order(self):
        product = Product.objects.get(id=1)
        order = Order.objects.get(id=1)
        feature_value = FeaturesValue.objects.get(id=1)
        product_order = ProductOrder.objects.create(product=product, order=order, count=1,
                                                    consume_location=ConsumeLocation.take_away,
                                                    feature_value=feature_value)
        serializer = ProductOrderFlatSerializer(product_order)
        response = client.post(reverse('client_order'), {'data': [serializer.data]})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_update_waiting_order(self):
        product = Product.objects.get(id=1)
        order = Order.objects.get(id=1)
        feature_value = FeaturesValue.objects.get(id=1)
        product_order = ProductOrder.objects.create(product=product, order=order, count=1,
                                                    consume_location=ConsumeLocation.take_away,
                                                    feature_value=feature_value)
        serializer = ProductOrderFlatSerializer(product_order)
        response = client.post(reverse('client_order', args=(1,)), {'data': [serializer.data]})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_update_not_waiting_order(self):
        product = Product.objects.get(id=1)
        user = User.objects.get(id=1)
        order = Order.objects.filter(user=user).exclude(state=OrderStatus.waiting).first()
        feature_value = FeaturesValue.objects.get(id=1)
        product_order = ProductOrder.objects.create(product=product, order=order, count=1,
                                                    consume_location=ConsumeLocation.take_away,
                                                    feature_value=feature_value)
        serializer = ProductOrderFlatSerializer(product_order)
        response = client.post(reverse('client_order', args=(order.id,)), {'data': [serializer.data]})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data.get('message'), 'Not valid order state')
        self.assertTrue(response.data.get('error'))

    def test_get_object_ok(self):
        user = User.objects.get(id=1)
        order = Order.objects.filter(user=user).first()
        returned_order, response_status = OrderView.get_object(order.id, user=user)
        self.assertEqual(returned_order, order)
        self.assertEqual(response_status, status.HTTP_200_OK)

    def test_get_object_403(self):
        user = User.objects.get(id=1)
        order = Order.objects.exclude(user=user).first()
        returned_order, response_status = OrderView.get_object(order.id, user=user)
        self.assertEqual(returned_order, None)
        self.assertEqual(response_status, status.HTTP_403_FORBIDDEN)

    def test_get_object_404(self):
        user = User.objects.get(id=1)
        returned_order, response_status = OrderView.get_object(1000, user=user)
        self.assertEqual(returned_order, None)
        self.assertEqual(response_status, status.HTTP_404_NOT_FOUND)



