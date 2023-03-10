import re

from django.forms import ValidationError

from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genres, Review, Title
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Validates User model."""

    class Meta:
        fields = [
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        ]
        model = User


class SignupSerializer(serializers.Serializer):
    """Validates Signup proccess."""

    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(max_length=150)

    def validate(self, data):
        email = data['email']
        username = data['username']
        if username == 'me':
            raise serializers.ValidationError(
                'Регистрация пользователя с именем "me" невозможна'
            )
        reg = re.compile(r'^[\w.@+-]+')
        if not reg.match(username):
            raise serializers.ValidationError(
                'Использованы недопустимые символы'
            )
        email_exists = User.objects.filter(email=email).exists()
        username_exists = User.objects.filter(username=username).exists()
        if email_exists and not username_exists:
            raise serializers.ValidationError(
                'Указанная почта уже зарегистрирована другим пользователем'
            )
        if username_exists and not email_exists:
            raise serializers.ValidationError(
                'Имя пользователя уже занято'
            )
        return data


class CategorySerializer(serializers.ModelSerializer):
    """Validates Category model."""

    slug = serializers.SlugField(
        max_length=50,
        validators=[
            UniqueValidator(queryset=Category.objects.all())
        ]
    )

    class Meta:
        fields = ['name', 'slug']
        model = Category
        lookup_field = 'slug'


class GenresSerializer(serializers.ModelSerializer):
    """Validates Genres model."""

    slug = serializers.SlugField(
        max_length=50,
        validators=[
            UniqueValidator(queryset=Genres.objects.all())
        ]
    )

    class Meta:
        fields = ['name', 'slug']
        model = Genres
        lookup_field = 'slug'


class TitleSerializer(serializers.ModelSerializer):
    """Validates Title model."""

    category = CategorySerializer()
    genre = GenresSerializer(many=True)
    rating = serializers.IntegerField()

    class Meta:
        fields = [
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        ]
        model = Title

    def get_genre(self, obj):
        genre_query = Genres.objects.filter(genre=obj.id)
        serializer = GenresSerializer(genre_query, many=True)
        return serializer.data


class TitleCreationSerializer(TitleSerializer):
    """Validates creating Title model."""

    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all(), required=True
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genres.objects.all(),
        required=True,
        many=True
    )

    class Meta:
        fields = ['id', 'name', 'year', 'description', 'genre', 'category']
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    """Validates Review model."""

    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
            request.method == 'POST'
            and Review.objects.filter(title=title, author=author).exists()
        ):
            raise ValidationError(
                'Пользователь может оставить только один отзыв!'
            )
        return data


class CheckConfCodeSerializer(serializers.Serializer):
    """Validates the proccess of getting Confirmation Code."""

    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()


class CommentSerializer(serializers.ModelSerializer):
    """Validates Comment model."""

    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date', 'review')
        model = Comment
