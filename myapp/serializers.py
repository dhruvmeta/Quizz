from rest_framework import serializers
from .models import *

class QuizSerializes(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text']

class QuestionSerializer(serializers.ModelSerializer):
     class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'quiz']
        
class AnswerSerializers(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['question', 'answer']

class usersubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubmission
        fields = ['user_name', 'quiz', 'score']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'tc']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            name=validated_data['name'],
            email=validated_data['email'],
            password=validated_data['password'],
            tc=validated_data.get('tc', False)  # ✅ include tc
        )
        return user
    
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'