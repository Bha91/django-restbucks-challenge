from django.db import models
from django.contrib.auth.models import User
from django.db.models import Manager


class ConsumeLocation(models.Model):
    """
    Type of order consumption chooses by the client.

    0- take_away
    1- in_shop
    """

    take_away = 0
    in_shop = 1
    types = (
        (take_away, 'take away'),
        (in_shop, 'in shop'),
    )


class OrderStatus(models.Model):
    """
    Type of Order Status.

    0- waiting: new orders, changing order by clients is available just in this state.
    1- preparation: choose by CoffeeShop manager to inform client.
    2- ready: choose by CoffeeShop manager to inform client.
    3- delivered: choose by CoffeeShop manager for finished orders.
    4- canceled: deleted orders by clients will have this state.
    """

    waiting = 0
    preparation = 1
    ready = 2
    delivered = 3
    canceled = 4
    types = (
        (waiting, 'waiting'),
        (preparation, 'preparation'),
        (ready, 'ready'),
        (delivered, 'delivered'),
        (canceled, 'canceled'),
    )


class Feature(models.Model):
    """
    Feature or option of products, multiple :model:`restbuck_app.Product` may have same feature.
    relation store in :model:`restbuck_app.ProductFeature`.
    """

    title: str = models.CharField(max_length=255, help_text="A display title for one product's feature")
    # TODO: change to 'display_name' and  unique 'code' to support multiple 'kind' for different product

    def __str__(self):
        return self.title


class FeaturesValue(models.Model):
    """
    Stores an option of one :model:`restbuck_app.Feature`.
    relation store in :model:`restbuck_app.ProductFeature`
    """

    feature: Feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    title: str = models.CharField(max_length=255, help_text="display title for an option of feature")

    def __str__(self):
        return self.feature.title+'-->'+self.title


class Product(models.Model):
    """
    Products Model. related to :model:`restbuck_app.Order`, :model:`restbuck_app.ProductFeature`
    """
    title: str = models.CharField(max_length=255, help_text="display title for a product")
    cost: int = models.IntegerField(help_text="cost of product")
    feature: Feature = models.ForeignKey(Feature, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.title


class ProductFeature(models.Model):
    """
    Relation of :model:`restbuck_app.Product` and  :model:`restbuck_app.Feature`
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)

    def __str__(self):
        return self.product.title+' '+self.feature.title


class ProductOrder(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    count = models.IntegerField()
    consume_location = models.SmallIntegerField(choices=ConsumeLocation.types)
    feature_value = models.ForeignKey(FeaturesValue, on_delete=models.PROTECT)

    def __str__(self):
        return self.count.__str__()+'*'+self.product.title+'--orderNo: '+self.order.id.__str__()


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    status = models.SmallIntegerField(choices=OrderStatus.types, default=OrderStatus.waiting)
    product_list = models.ManyToManyField(Product, through=ProductOrder, related_name='products')

    def __str__(self):
        return 'id:'+self.id.__str__() + '-' + self.user.__str__() + '-' + ', '.join([x.title for x in self.product_list.all()])

