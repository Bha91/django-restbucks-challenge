from django.core.mail import send_mail
from django.db import models
from django.contrib.auth.models import User
from django_restbucks_challenge.settings import EMAIL_SENDER_NOREPLAY


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
    """

    waiting = 0
    preparation = 1
    ready = 2
    delivered = 3
    types = (
        (waiting, 'waiting'),
        (preparation, 'preparation'),
        (ready, 'ready'),
        (delivered, 'delivered'),
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

    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    title: str = models.CharField(max_length=255, help_text="display title for an option of feature")

    def __str__(self):
        return self.feature.title + '-->' + self.title


class Product(models.Model):
    """ Products Model. related to :model:`restbuck_app.Order`, :model:`restbuck_app.ProductFeature` """

    title: str = models.CharField(max_length=255, help_text="display title for a product")
    cost: int = models.IntegerField(help_text="cost of product")
    feature = models.ForeignKey(Feature, null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.title


class ProductOrder(models.Model):
    """ each item of client order. an :model:`restbuck_app.Order` can have multiple ProductOrder """

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    count = models.IntegerField(help_text="number of product client ordered")
    consume_location = models.SmallIntegerField(choices=ConsumeLocation.types)
    feature_value = models.ForeignKey(FeaturesValue, on_delete=models.PROTECT, help_text="ordered option of product",
                                      null=True, blank=True)

    def __str__(self):
        return self.count.__str__() + '*' + self.product.title + '--orderNo: ' + self.order.id.__str__()


class Order(models.Model):
    """ Store a Client order. """

    user = models.ForeignKey(User, on_delete=models.PROTECT, help_text="client")
    state = models.SmallIntegerField(choices=OrderStatus.types, default=OrderStatus.waiting, help_text="state of order")
    previous_state = models.SmallIntegerField(choices=OrderStatus.types, default=OrderStatus.waiting,
                                              help_text="previous state of order")
    product_list = models.ManyToManyField(Product, through=ProductOrder, related_name='products',
                                          help_text="list of products client ordered")
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return 'id:' + self.id.__str__() + '-' + \
               self.user.__str__() + '-' + \
               ', '.join([x.title for x in self.product_list.all()])

    def save(self, *args, **kwargs):
        """ override default save method to notify user on state change."""
        # TODO: function extraction and notify class
        if self.previous_state != self.state:
            email_subject = 'Order state changed!'
            email_body = 'your order numbered {} has been changed from {} state to {}.\n Best\nRestBucks CoffeeShop'
            send_mail(
                email_subject,
                email_body.format(self.id, self.get_previous_state_display(), self.get_state_display()),
                EMAIL_SENDER_NOREPLAY,
                [self.user.email],
                fail_silently=False,
            )
            self.previous_state = self.state
        return super(Order, self).save(*args, **kwargs)


