from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from restbuck_app.models import *


class FeatureValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeaturesValue
        fields = ('id', 'title')


class FeatureValueWithLabelSerializer(serializers.ModelSerializer):
    feature_title = serializers.CharField(source='feature.title', read_only=True)
    value = serializers.CharField(source='title', read_only=True)

    class Meta:
        model = FeaturesValue
        fields = ('id', 'value', 'feature_title')


class FeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feature
        fields = ('title',)


class FeatureWithValuesSerializer(serializers.ModelSerializer):
    value_list = SerializerMethodField(read_only=True)

    class Meta:
        model = Feature
        fields = ('title', 'value_list')

    def get_value_list(self, obj):
        values = obj.featuresvalue_set.all()
        serialized_fv = FeatureValueSerializer(values, many=True, read_only=True).data
        return serialized_fv


class ProductSerializer(serializers.ModelSerializer):
    feature_list = FeatureWithValuesSerializer(read_only=True, many=True)
    consume_location = serializers.SerializerMethodField()
    # TODO: check standard serializer for choices

    class Meta:
        model = Product
        fields = ('id',
                  'title',
                  'cost',
                  'consume_location',
                  'feature_list')

    def get_consume_location(self, obj):
        return ConsumeLocation.types


class ProductOrderSerializer(serializers.HyperlinkedModelSerializer):

    product = serializers.ReadOnlyField(source='product.title')
    consume_location = serializers.CharField(source='get_consume_location_display')

    class Meta:
        model = ProductOrder
        fields = ('product', 'count', 'consume_location')


class OrderSerializer(serializers.ModelSerializer):
    product_list = ProductOrderSerializer(source='productorder_set', read_only=True, many=True)
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Order
        fields = ('id', 'status', 'product_list')