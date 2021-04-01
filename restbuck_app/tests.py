from distutils.command.install import install

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

    # TODO: Test get & delete orders already deleted before

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


class FeatureValueSerializerTest(TestCase):
    def setUp(self) -> None:
        size_feature = Feature.objects.create(title='size')
        self.feature_value_attributes = {
            'id': 1,
            'title': 'big',
            'feature': size_feature
        }

        self.feature_value = FeaturesValue.objects.create(**self.feature_value_attributes)
        self.serializer = FeatureValueSerializer(instance=self.feature_value)

    def test_contains_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'title'])

    def test_title_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['title'], self.feature_value_attributes['title'])

    def test_id_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['id'], self.feature_value_attributes['id'])


class FeatureWithValuesSerializerTest(TestCase):
    def setUp(self) -> None:
        self.feature_attributes = {
            'title': 'size'
        }
        self.feature = Feature.objects.create(**self.feature_attributes)
        self.serializer = FeatureWithValuesSerializer(instance=self.feature)
        self.feature_value_big = FeaturesValue.objects.create(feature=self.feature, title='big')
        self.feature_value_small = FeaturesValue.objects.create(feature=self.feature, title='small')

    def test_contain_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['title', 'value_list'])

    def test_title_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['title'], self.feature_attributes['title'])

    def test_value_list_field_content(self):
        data = self.serializer.data
        values = self.feature.featuresvalue_set.all()
        serialized_fv = FeatureValueSerializer(values, many=True, read_only=True).data
        self.assertEqual(data['value_list'], serialized_fv)


class ProductSerializerTest(TestCase):
    def setUp(self) -> None:
        self.feature = Feature.objects.create(title='size')
        self.feature_value_big = FeaturesValue.objects.create(feature=self.feature, title='big')
        self.feature_value_small = FeaturesValue.objects.create(feature=self.feature, title='small')
        self.product_attributes = {
            'title': 'water',
            'cost': 2,
            'id': 1,
            'feature': self.feature
        }
        self.product = Product.objects.create(**self.product_attributes)
        self.serializer = ProductSerializer(instance=self.product)

    def test_contain_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id',
                                            'title',
                                            'cost',
                                            'consume_location',
                                            'feature'])

    def test_title_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['title'], self.product_attributes['title'])

    def test_cost_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['cost'], self.product_attributes['cost'])

    def test_id_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['id'], self.product_attributes['id'])

    def test_consume_location_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['consume_location'], ConsumeLocation.types)

    def test_feature_field_content(self):
        data = self.serializer.data
        serialized_feature = FeatureWithValuesSerializer(self.feature).data
        self.assertEqual(data['feature'], serialized_feature)


class ProductOrderFlatSerializerTest(TestCase):
    def setUp(self) -> None:
        self.feature = Feature.objects.create(title='size')
        self.feature_value_big = FeaturesValue.objects.create(feature=self.feature, title='big')
        self.feature_value_small = FeaturesValue.objects.create(feature=self.feature, title='small')
        self.product = Product.objects.create(title='water', cost=2, feature=self.feature)
        self.product_tea = Product.objects.create(title='tea', cost=5)
        self.user = User.objects.create(username='test1', password='Ronash#1234')
        self.order = Order.objects.create(user=self.user)
        self.product_order_attributes = {
            'product': self.product,
            'order': self.order,
            'count': 1,
            'consume_location': ConsumeLocation.take_away,
            'feature_value': self.feature_value_big
        }
        self.product_order = ProductOrder.objects.create(**self.product_order_attributes)
        self.serializer = ProductOrderFlatSerializer(instance=self.product_order)

    def test_contain_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['product', 'product_title', 'count', 'consume_location',
                                            'consume_location_display', 'feature_value', 'feature_value_title'])

    def test_product_title_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['product_title'], self.product_order_attributes['product'].title)

    def test_product_id_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['product'], self.product_order_attributes['product'].id)

    def test_count_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['count'], self.product_order_attributes['count'])

    def test_consume_location_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['consume_location'], self.product_order_attributes['consume_location'])

    def test_feature_value_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['feature_value'], self.product_order_attributes['feature_value'].id)

    def test_feature_value_title_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['feature_value_title'], self.product_order_attributes['feature_value'].title)


class OrderSerializerTest(TestCase):
    def setUp(self) -> None:
        self.feature = Feature.objects.create(title='size')
        self.feature_value_big = FeaturesValue.objects.create(feature=self.feature, title='big')
        self.product = Product.objects.create(title='water', cost=2, feature=self.feature)
        self.user = User.objects.create(username='test1', password='Ronash#1234')
        self.order_attributes = {
            'user': self.user
        }
        self.order = Order.objects.create(**self.order_attributes)
        self.product_order = ProductOrder.objects.create(product=self.product, order=self.order, count=1,
                                                         consume_location=ConsumeLocation.take_away,
                                                         feature_value=self.feature_value_big)
        self.serializer = OrderSerializer(instance=self.order)

    def test_contain_expected_fields(self):
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'state', 'product_list'])

    def test_id_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['id'], self.order.id)

    def test_state_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['state'], self.order.get_state_display())

    def test_product_list_field_content(self):
        data = self.serializer.data
        self.assertEqual(data['product_list'], ProductOrderFlatSerializer(self.order.productorder_set, read_only=True,
                                                                          many=True).data)
