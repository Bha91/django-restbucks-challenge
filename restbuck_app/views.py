from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404
from restbuck_app.models import *
from restbuck_app.serializers import *


class Menu(APIView):
    def get(self, request):
        products = Product.objects.all()
        data = []
        for product in products:
            data.append(ProductSerializer(product).data)
        return Response({'data': data,
                         'error': False})


def get_auth_user(request):
    return User.objects.get(id=1)


class OrderView(APIView):
    def get_object(self, pk, user):
        if Order.objects.filter(pk=pk).exclude(status=OrderStatus.canceled).exists():
            order = Order.objects.get(pk=pk)
            response_status = status.HTTP_200_OK
            if order.user != user:
                response_status = status.HTTP_403_FORBIDDEN
            return order, response_status
        else:
            return None, status.HTTP_404_NOT_FOUND

    def get(self, request, pk=0):
        user = get_auth_user(request)
        if pk > 0:
            order, response_status = self.get_object(pk, user)
            if response_status == status.HTTP_404_NOT_FOUND:
                return Response({'error': True, 'message': 'requested order dose not exist'}, response_status)
            elif response_status == status.HTTP_403_FORBIDDEN:
                return Response({'error': True, 'message': 'Not your order'}, response_status)
            elif response_status == status.HTTP_200_OK:
                data = OrderSerializer(order).data
        elif pk < 0:
            return Response({'error': True, 'message': 'Not valid order id'}, status.HTTP_400_BAD_REQUEST)
        else:
            orders = Order.objects.filter(user=user)
            data = []
            for order in orders:
                data.append(OrderSerializer(order).data)
        return Response({'data': data,
                         'error': False})

    def delete(self, request, pk=0):
        user = get_auth_user(request)
        if pk > 0:
            order, response_status = self.get_object(pk, user)
            if response_status == status.HTTP_404_NOT_FOUND:
                return Response({'error': True, 'message': 'requested order dose not exist'}, response_status)
            elif response_status == status.HTTP_403_FORBIDDEN:
                return Response({'error': True, 'message': 'Not your order'}, response_status)
            elif response_status == status.HTTP_200_OK:
                if order.status == OrderStatus.waiting:
                    order.status = OrderStatus.canceled
                    order.save()
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response({'error': True, 'message': 'Not valid order status'}, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': True, 'message': 'Not valid order id'}, status.HTTP_400_BAD_REQUEST)
