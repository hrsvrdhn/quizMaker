# Adds topics to a candidate object based on passed tests taken

def addTopicToCandidate():
    from quiz.models import TestStat

    for teststat in TestStat.objects.all():
        topics = teststat.test.topics.all()
        candidate = teststat.candidate
        candidate_topics = candidate.topics
        for topic in topics:
            if candidate_topics.filter(pk=topic.pk).exists():
                continue
            candidate_topics.add(topic)
            candidate.save()

def sendMails():
    from accounts.models import UserProfile
    from quiz.models import Test
    for userProfile in UserProfile.objects.all():
        recommendedTests = Test.objects.recommended(user_profile)
        sendRecommendationTestEmail(userProfile, recommendedTests)
        