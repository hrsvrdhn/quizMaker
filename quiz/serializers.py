from rest_framework import serializers
from .models import Test, Question, QuestionStat

class TestSerializer(serializers.ModelSerializer):
	owner = serializers.CharField(source="owner.user.extra_data.name", read_only=True)
	rating = serializers.FloatField(source="get_average_rating", read_only=True)
	topics = serializers.StringRelatedField(many=True)
	attempts = serializers.IntegerField(source="get_attempts", read_only=True)
	class Meta:
		model = Test
		fields =  ('id', 'name', 'created_on', 'owner', 'attempts', 'rating', 'topics', 'negative_marking')

class QuestionSerializer(serializers.ModelSerializer):
	test = serializers.PrimaryKeyRelatedField(read_only=True)
	class Meta:
		model = Question
		exclude = ('is_active',)

class QuestionListSerializer(QuestionSerializer):
	update_url = serializers.URLField(source='get_update_url')
	option1 = serializers.CharField(source='wrong_answer_1', read_only=True)
	option2 = serializers.CharField(source='wrong_answer_2', read_only=True)
	option3 = serializers.CharField(source='wrong_answer_3', read_only=True)
	option4 = serializers.CharField(source='correct_answer', read_only=True)
	class Meta:
		model = Question
		fields = ('question', 'update_url', 'option1', 'option2', 'option3', 'option4')

class QuestionStatSerializer(serializers.ModelSerializer):
	question = serializers.PrimaryKeyRelatedField(read_only=True)
	correct_answer = serializers.CharField(default=None)
	class Meta:
		model = QuestionStat
		exclude = ('candidate', 'is_correct')

class CorrectAnswerSerialize(serializers.ModelSerializer):
	class Meta:
		model = Question
		fields = ('correct_answer')

class TestSerializerForHome(serializers.ModelSerializer):
	owner = serializers.CharField(source="owner.user.extra_data.name", read_only=True)
	owner_username = serializers.CharField(source="owner.user.user.username", read_only=True)	
	rating = serializers.FloatField(source="get_average_rating", read_only=True)
	topics = serializers.StringRelatedField(many=True)
	attempts = serializers.IntegerField(source="get_attempts", read_only=True)
	date_created = serializers.SerializerMethodField('get_created_date')
	
	def get_created_date(self, obj):
		return obj.created_on.date()

	class Meta:
		model = Test
		fields =  ('id', 'name', 'date_created', 'owner_username', 'owner', 'attempts', 'rating', 'topics')
	
