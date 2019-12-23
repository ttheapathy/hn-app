from rest_framework import generics, filters, serializers, exceptions, mixins
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings

from .models import Post
from .tasks import fetch_posts


class PaginatedValidationMixin(mixins.ListModelMixin):

    def get_paginated_response(self, data):
        order, limit, offset = map(self.request.query_params.get, ['order', 'limit', 'offset'])

        if order is not None and order.lstrip('-') not in self.ordering_fields:
            raise exceptions.ValidationError(
                'Order must be one of {0}'.format(', '.join(self.ordering_fields))
            )

        try:
            limit, offset = map(lambda param: int(param) if param is not None else None, [limit, offset])
        except ValueError:
            raise exceptions.ValidationError(
                'Limit and offset must be integer'
            )

        if limit is not None and not (0 <= limit <= settings.MAX_PAGE_SIZE):
            raise exceptions.ValidationError(
                'Limit must be between 0 and {0}'.format(settings.MAX_PAGE_SIZE)
            )

        if offset is not None and offset < 0:
            raise serializers.ValidationError(
                'Offset must be greater than 0'
            )

        return Response(data)


class PostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'url', 'created']


class PostListView(generics.ListAPIView, PaginatedValidationMixin):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    filter_backends = (filters.OrderingFilter, )
    ordering_fields = ['id', 'title', 'url', 'created']


class PostFetch(APIView):
    def get(self, request, format=None):
        try:
            fetch_posts()
        except Exception as error:
            return Response('Fetch new posts failed. Error {}.'.format(error), status=500)
        return Response('Fetch new posts has been complete.')
