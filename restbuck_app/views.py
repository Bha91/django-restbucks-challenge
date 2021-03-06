import rest_framework
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404
from restbuck_app.models import *
from restbuck_app.serializers import *


# TODO: user GenericAPIView or better GenericViewSet
class Menu(APIView):
    """ handle list of products for client order """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """ GET: all product with their feature and features values """
        products = Product.objects.all()
        data = ProductSerializer(products, many=True).data
        return Response({'data': data,
                         'error': False})


def get_auth_user(request):
    """ get authenticated user"""
    return request.user


# TODO: user GenericAPIView or better GenericViewSet
class OrderView(APIView):
    """ handle client order API """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @staticmethod
    def get_object(pk: int, user: User):
        """ get order by id and check if is related to request user.

        :param user: Order owner, an User onject
        :param pk: primary key or id of Order.
        :returns: Order object (or None if can not find related object) and  status code to return to user.
        :rtype: Order
        :rtype: rest_framework.status
        """
        if Order.objects.filter(pk=pk, is_deleted=False).exists():
            order = Order.objects.get(pk=pk)
            response_status = status.HTTP_200_OK
            if order.user != user:
                response_status = status.HTTP_403_FORBIDDEN
                order = None
            return order, response_status
        else:
            return None, status.HTTP_404_NOT_FOUND

    def get(self, request, pk=0):
        """ GET: user's order by id, or all of his order if no pk provided

        :param request: API request
        :param pk: primary key or id of Order.
        :type pk: int
        :return: API response data and status code
        """
        data = []
        user = get_auth_user(request)
        if pk > 0:
            order, response_status = self.get_object(pk, user)
            # TODO: need help, use DRF tools like "get or 404"
            if response_status == status.HTTP_404_NOT_FOUND:
                return Response({'error': True, 'message': 'requested order dose not exist'}, response_status)
            # TODO: use has_object_permission for 403
            elif response_status == status.HTTP_403_FORBIDDEN:
                return Response({'error': True, 'message': 'Not your order'}, response_status)
            elif response_status == status.HTTP_200_OK:
                data = OrderSerializer(order).data
        elif pk < 0:
            return Response({'error': True, 'message': 'Not valid order id'}, status.HTTP_400_BAD_REQUEST)
        else:
            orders = Order.objects.filter(user=user, is_deleted=False)
            for order in orders:
                data.append(OrderSerializer(order).data)
        # TODO: check for empty product list
        return Response({'data': data,
                         'error': False})

    def delete(self, request, pk=0):
        """ DELETE: user can delete his waiting order by id.

        :param request: API request
        :param pk: primary key or id of Order.
        :type pk: int
        :return: API response data and status code
        """
        user = get_auth_user(request)
        if pk > 0:
            order, response_status = self.get_object(pk, user)
            if response_status == status.HTTP_404_NOT_FOUND:
                return Response({'error': True, 'message': 'requested order dose not exist'}, response_status)
            elif response_status == status.HTTP_403_FORBIDDEN:
                return Response({'error': True, 'message': 'Not your order'}, response_status)
            elif response_status == status.HTTP_200_OK:
                if order.state == OrderStatus.waiting:
                    order.is_deleted = True
                    order.save()
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response({'error': True, 'message': 'Not valid order state'}, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': True, 'message': 'Not valid order id'}, status.HTTP_400_BAD_REQUEST)

    def post(self, request, pk=0):
        """
        POST: new order of user or change 'waiting' order.

        :param request: API request
        :param pk: primary key or id of Order.
        :type pk: int
        :return: API response data and status code
        """
        user = get_auth_user(request)
        order = None
        if pk > 0:
            order, response_status = self.get_object(pk, user)
            if response_status == status.HTTP_404_NOT_FOUND:
                return Response({'error': True, 'message': 'requested order dose not exist'}, response_status)
            elif response_status == status.HTTP_403_FORBIDDEN:
                return Response({'error': True, 'message': 'Not your order'}, response_status)
            elif order.state != OrderStatus.waiting:
                return Response({'error': True, 'message': 'Not valid order state'}, status.HTTP_400_BAD_REQUEST)
        elif pk < 0:
            return Response({'error': True, 'message': 'Not valid order id'}, status.HTTP_400_BAD_REQUEST)
        data = request.data.get('data')
        serializer = ProductOrderFlatSerializer(data=data, many=True)
        if serializer.is_valid():
            if order is None:
                order = Order.objects.create(user=user)
            # TODO: must be changed for production, specially without log due to the possibility of Integrity
            tobe_deleted = ProductOrder.objects.filter(order=order)
            if tobe_deleted.exists():
                tobe_deleted.delete()
            serializer.save(order=order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': True, 'message': serializer.errors[0]}, status=status.HTTP_400_BAD_REQUEST)
