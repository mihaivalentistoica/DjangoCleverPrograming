import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question

def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)  


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    
    def test_past_question(self):
        create_question(question_text='Past question', days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], 
            ['<Question: Past question>'])


    def test_future_question(self):
        create_question(question_text='Future question', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [])


    def test_future_and_past_question(self):
        create_question(question_text='Future question', days=30)
        create_question(question_text='Past question', days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],
            ['<Question: Past question>'])


    def test_tow_past_question(self):
        create_question(question_text='Past question 1', days=-30)
        create_question(question_text='Past question 2', days=0)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], 
            ['<Question: Past question 2>', '<Question: Past question 1>'])


class QuestionDetailsViewTest(TestCase):
    def test_future_questions(self):
        future_question = create_question(question_text='Future question', days=5)
        response = self.client.get(reverse('polls:details', args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)


    def test_past_question(self):
        past_question = create_question(question_text='Past question', days=0)
        response = self.client.get(reverse('polls:details', args=(past_question.id,)))   
        self.assertContains(response, past_question.question_text)


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        time = timezone.now()
        future_question = Question(pub_date=time + datetime.timedelta(30))
        self.assertIs(future_question.was_published_recently(), False)


    def test_was_published_recently_with_older_question(self):
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_quetion = Question(pub_date=time)
        self.assertIs(old_quetion.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)