from django.db import models

class TestManager(models.Manager):
    def recommended(self, user):
        return (
            self.get_queryset()
            .filter(topics__in=user.topics.all())
            .distinct()
            .exclude(owner=user)
            .exclude(private=True)
            .exclude(attempts__in=TestStat.objects.filter(candidate=user))
            .distinct()
        )

class QuestionManager(models.Manager):
    def questionListByTest(self, test):
        return (
            self.get_queryset()
            .filter(test=test)
        )
