import datetime
from datetime import timedelta
from django.core.validators import RegexValidator
from rest_framework import serializers
from .models import *


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["name", "email", "password"]

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            name=validated_data["name"],
            username=validated_data["email"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email', 'image']


class SubscriptionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ['id', 'subscription', 'is_active', 'payment_date', 'expiry_date', 'amount', 'subscription_map_id']


class SubscriptionSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'subscription', 'amount', 'expiry_date', 'is_active', 'payment_date', 'description']


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    subscription_id = serializers.IntegerField(write_only=True)
    subscription = serializers.CharField(source='get_subscription_display', read_only=True)

    class Meta:
        model = Subscription
        fields = ['subscription_id', 'subscription', 'amount', 'expiry_date', 'is_active', 'payment_date', 'description', 'subscription_map_id']
        extra_kwargs = {
            'amount': {'required': False},
            'expiry_date': {'required': False},
            'is_active': {'required': False},
            'payment_date': {'required': False},
            'description': {'required': False},
            'subscription_map_id': {'required': False},
        }

    SUBSCRIPTION_ID_MAP = {
        1: 'free',
        2: 'monthly',
        3: 'yearly',
    }

    def create(self, validated_data):
        subscription_id = validated_data.pop('subscription_id')
        subscription_type = self.SUBSCRIPTION_ID_MAP.get(subscription_id)

        if not subscription_type:
            raise serializers.ValidationError("Invalid subscription ID.")

        validated_data['subscription'] = subscription_type
        validated_data['subscription_map_id'] = subscription_id  # Set the subscription_map_id

        payment_date = datetime.now().date()

        if subscription_type == 'free':
            expiry_date = payment_date + timedelta(days=14)
            description = "Free"
        elif subscription_type == 'monthly':
            expiry_date = payment_date + timedelta(days=30)
            description = "Full Customisation and Tracking"
        elif subscription_type == 'yearly':
            expiry_date = payment_date + timedelta(days=365)
            description = "Full Customisation and Tracking"
        else:
            expiry_date = payment_date  # Default case, although ideally, this shouldn't be hit
            description = "No description available"

        validated_data['expiry_date'] = expiry_date
        validated_data['payment_date'] = payment_date
        validated_data['description'] = description

        subscription = super().create(validated_data)
        return subscription

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return representation


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']


class ScoresSerializer(serializers.ModelSerializer):
    selected_emotions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Emotion.objects.all()
    )

    class Meta:
        model = Scores
        fields = ['user', 'image_value', 'general_emotion_value', 'revaluation_one', 'revaluation_two',
                  'selected_emotions']
        extra_kwargs = {
            'user': {'required': False}
        }

    def create(self, validated_data):
        selected_emotions = validated_data.pop('selected_emotions', [])
        scores = Scores.objects.create(**validated_data)
        scores.selected_emotions.set(selected_emotions)
        return scores

    def update(self, instance, validated_data):
        selected_emotions = validated_data.pop('selected_emotions', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        instance.selected_emotions.set(selected_emotions)
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user.name  # Assuming you want to show the username instead of the user ID
        representation['selected_emotions'] = [emotion.name for emotion in instance.selected_emotions.all()]
        return representation


class ScoreRecordSerializer(serializers.ModelSerializer):
    selected_emotions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Emotion.objects.all()
    )

    class Meta:
        model = ScoreRecord
        fields = ['image_value', 'general_emotion_value', 'revaluation_one', 'revaluation_two', 'selected_emotions',
                  'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['selected_emotions'] = [emotion.name for emotion in instance.selected_emotions.all()]
        return representation


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r'^[\w.@+\-\s]+$',
                message="Enter a valid name. This value may contain only letters, numbers, and @/./+/-/_/ spaces characters."
            )
        ]
    )

    class Meta:
        model = CustomUser
        fields = ['name', 'image']