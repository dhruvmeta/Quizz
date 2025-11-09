from django.urls import path
from myapp import views 
from .views import *


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='register'),
    path('quizzes/', views.quiz_list, name='quiz_list'),
    path('quiz/<int:quiz_id>/', views.quiz_attempt, name='quiz_attempt'),
    path('quiz_history/', views.quiz_history, name='quiz_history'),
    path('add_question/', views.question, name='add_question'),
    path('upcoming_events/', views.upcomming_events, name='upcoming_events'),
    #---------------------------API Paths---------------------------#
    path('api/login/', LoginView.as_view(), name='api_login'),
    path('api/register/', userregister.as_view(), name='api_register'),
    path('api/quiz/',QuizListView.as_view()),
    path('api/questions/<int:pk>/',QuestionListView.as_view()),
    path('api/answers/<int:quiz_id>/',AnswerListView.as_view()),
    path('api/quiz/<int:quiz_id>/questions/',QuizQuestionsAPIView.as_view(), name='api_get_quiz_questions'),
    path('api/quiz/<int:quiz_id>/submit/', QuizSubmitAPIView.as_view(), name='api_submit_quiz'),
    path('api/quiz_history/', QuizeHistoryView.as_view(), name='api_quiz_history'),
    path('api/add_question/', AddquestionAPIView.as_view(), name='api_add_question'),
    path('api/events/', EventListView.as_view(), name='api_events'),
]
