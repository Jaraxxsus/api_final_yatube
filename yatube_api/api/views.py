# TODO:  Напишите свой вариант
from django.shortcuts import get_object_or_404
from rest_framework import serializers, viewsets, filters

from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework import mixins
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .permissons import IsAuthorOrReadOnly
from .serializers import PostSerializer, GroupSerializer, CommentSerializer, FollowSerializer
from posts.models import Post, Group, Follow


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly)
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

class GroupViewSet(ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly)

    def get_post_by_url(self):
        return get_object_or_404(Post, pk=self.kwargs.get("post_id"))

    def get_queryset(self):
        post = self.get_post_by_url()
        return post.comments.all()

    def perform_create(self, serializer):
        serializer.save(
            post=self.get_post_by_url(),
            author=self.request.user
        )

class FollowViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('following__username',)

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if serializer.validated_data["following"] == self.request.user:
            raise serializers.ValidationError(
                "Нельзя подписываться на себя"
            )
        serializer.save(
            user=self.request.user
        )








