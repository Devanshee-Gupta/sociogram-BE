from rest_framework.serializers import ModelSerializer
from home.models import *

class UsersSerializer(ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'


class PostSerializer(ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'


class SavedCollectionSerializer(ModelSerializer):
    class Meta:
        model = SavedCollection
        fields = '__all__'

class SavedItemSerializer(ModelSerializer):
    class Meta:
        model = SavedItem
        fields = '__all__' 