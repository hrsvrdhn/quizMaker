import bleach
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum
from django.urls import reverse

from accounts.models import UserProfile
from topic.models import Topic


# Create your models here.

####################################################################################################333


class TestManager(models.Manager):
    def recommended(self, user):
        return (
            self.get_queryset()
            .filter(topics__in=user.topics.all())
            .distinct()
            .exclude(owner=user)
            .exclude(private=True)
            .exclude(publish=False)
            .exclude(is_active=False)
            .exclude(attempts__in=TestStat.objects.filter(candidate=user))
            .distinct()
        )

    def getTestByOwner(self, owner):
        return self.get_queryset().filter(owner=owner)


class Test(models.Model):
    name = models.CharField(max_length=500, blank=False, default="Sample Test")
    owner = models.ForeignKey(
        UserProfile, related_name="tests", null=True, on_delete=models.SET_NULL
    )
    topics = models.ManyToManyField(Topic, blank=True, related_name="tests")
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    publish = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    published_on = models.DateTimeField(null=True)
    negative_marking = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    private = models.BooleanField(default=False)
    private_key = models.CharField(max_length=200, blank=True, null=True)

    DIFFICULTY_CHOICES = [
        ('EASY', 'EASY'),
        ('MEDIUM', 'MEDIUM'),
        ('HARD', 'HARD'),
    ]

    difficulty = models.CharField(
        max_length=6,
        choices=DIFFICULTY_CHOICES,
        default='MEDIUM'
    )

    objects = TestManager()

    def get_test_taking_url(self):
        url = reverse("quiz:takeQuiz", args=[self.pk])
        if self.private:
            url = "{}?token={}".format(url, self.private_key)
        return url

    def get_absolute_url(self):
        return reverse("quiz:manageTest", args=[self.id])

    def get_test_detail_url(self):
        url = reverse("quiz:testDetail", args=[self.id])
        if self.private:
            url = "{}?token={}".format(url, self.private_key)
        return url

    def get_average_rating(self):
        try:
            return round(
                self.feedbacks.aggregate(Sum("rating")).get("rating__sum")
                / self.feedbacks.count(),
                1,
            )
        except:
            return None

    def get_attempts(self):
        return self.attempts.all().count()

    def get_question_count(self):
        return self.questions.all().count()

    def __str__(self):
        return self.name


####################################################################################################333


class Question(models.Model):
    test = models.ForeignKey(Test, related_name="questions", on_delete=models.CASCADE)
    question = models.TextField(max_length=2000, blank=False)
    wrong_answer_1 = models.CharField(max_length=500, blank=False, null=False)
    wrong_answer_2 = models.CharField(max_length=500, blank=True, null=True)
    wrong_answer_3 = models.CharField(max_length=500, blank=True, null=True)
    correct_answer = models.CharField(max_length=500, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.question

    def get_update_url(self):
        return reverse(
            "quiz:updateQuestion", kwargs={"tpk": self.test.id, "qpk": self.id}
        )

    def save(self, *args, **kwargs):
        options_set = {self.wrong_answer_1, self.wrong_answer_2, self.wrong_answer_3, self.correct_answer}
        if not len(options_set) == 4:
            raise ValidationError("All options must be unique")
        super(Question, self).save(*args, **kwargs)


####################################################################################################333


class TestStat(models.Model):
    test = models.ForeignKey(
        Test, related_name="attempts", null=True, on_delete=models.SET_NULL
    )
    candidate = models.ForeignKey(
        UserProfile, related_name="teststats", on_delete=models.CASCADE
    )
    has_completed = models.BooleanField(default=False)
    date_taken = models.DateTimeField(auto_now_add=True)
    score = models.DecimalField(max_digits=9, decimal_places=6, null=True)

    def get_total_attempts(self):
        return QuestionStat.objects.filter(
            question__in=self.test.questions.all(), candidate=self.candidate
        ).count()

    def get_wrong_response_count(self):
        if self.has_completed:
            return (
                QuestionStat.objects.filter(
                    question__in=self.test.questions.all(),
                    candidate=self.candidate,
                    is_correct=False,
                    response__isnull=False,
                )
                .exclude(response__exact="")
                .count()
            )
        return None

    def get_round_off_score(self):
        if not self.score:
            return 0
        return round(self.score, 2)

    def get_correct_response_count(self):
        if self.has_completed:
            return QuestionStat.objects.filter(
                question__in=self.test.questions.all(),
                candidate=self.candidate,
                is_correct=True,
            ).count()
        return None

    def save(self, *args, **kwargs):
        if self.has_completed:
            self.score = QuestionStat.objects.filter(
                question__in=self.test.questions.all(),
                candidate=self.candidate,
                is_correct=True,
            ).count()
            try:
                self.score -= (
                    QuestionStat.objects.filter(
                        question__in=self.test.questions.all(),
                        candidate=self.candidate,
                        is_correct=False,
                        response__isnull=False,
                    )
                    .exclude(response__exact="")
                    .count()
                    / self.test.negative_marking
                )
            except:
                pass
        super(TestStat, self).save(*args, **kwargs)

    def __str__(self):
        return "{}-{}".format(self.test, "Stat")


####################################################################################################333


class QuestionStat(models.Model):
    question = models.ForeignKey(
        Question, related_name="question_history", null=True, on_delete=models.SET_NULL
    )
    candidate = models.ForeignKey(
        UserProfile, related_name="questionstat", null=True, on_delete=models.CASCADE
    )
    response = models.CharField(max_length=500, blank=True)
    is_correct = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.response == bleach.clean(self.question.correct_answer):
            self.is_correct = True
        super(QuestionStat, self).save(*args, **kwargs)

    def __str__(self):
        return "{}-{}".format(self.question.question, "stat")


####################################################################################################333


class Feedback(models.Model):
    rating = models.IntegerField(default=0)
    test = models.ForeignKey(Test, related_name="feedbacks", on_delete=models.CASCADE)
    candidate = models.ForeignKey(
        UserProfile, related_name="candidate_feedback", on_delete=models.CASCADE
    )
    message = models.CharField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return self.test.name


####################################################################################################333


class Comment(models.Model):
    test = models.ForeignKey(Test, related_name="comments", on_delete=models.CASCADE)
    candidate = models.ForeignKey(
        UserProfile, related_name="candidate_comments", on_delete=models.CASCADE
    )
    message = models.CharField(max_length=2000)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
