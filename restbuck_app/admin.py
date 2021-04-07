from django.contrib import admin
from restbuck_app.models import *
# TODO: do not repeat list_display for all class
# TODO: put registers together or use decorator


class FeatureAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Feature._meta.fields]


admin.site.register(Feature, FeatureAdmin)


class FeaturesValueAdmin(admin.ModelAdmin):
    list_display = [f.name for f in FeaturesValue._meta.fields]


admin.site.register(FeaturesValue, FeaturesValueAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Product._meta.fields]


admin.site.register(Product, ProductAdmin)


class ProductOrderInline(admin.TabularInline):
    model = ProductOrder
    extra = 1


class OrderAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Order._meta.fields]
    inlines = (ProductOrderInline,)


admin.site.register(Order, OrderAdmin)


class ProductOrderAdmin(admin.ModelAdmin):
    list_display = [f.name for f in ProductOrder._meta.fields]


admin.site.register(ProductOrder, ProductOrderAdmin)


