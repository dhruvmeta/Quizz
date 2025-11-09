from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate



# Create your views here.


def signup_view(request):
    return render(request, 'register.html')

def login_view(request):
    return render(request, 'login.html')

def home(request):
    return render(request,'home.html')

def quiz_history(request):
    return render(request,'quiz_history.html')

def question(request):
    return render(request, 'add_question.html')

def upcomming_events(request):
    return render(request, 'upcoming_events.html')
def quiz_list(request):
    quizzes = Quiz.objects.all()
    return render(request, 'quiz_list.html', {'quizzes': quizzes})

#----------------------------  API Views---------------------------#

# Token generater
def get_tokens_for_user(user):
    if not user.is_active:
      raise AuthenticationFailed("User is not active")

    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class userregister(APIView):
    def post(self,request):
        serializers=UserSerializer(data=request.data)
        if serializers.is_valid():
            password=serializers.validated_data['password']
            serializers.validated_data['password']=make_password(password)
            emp=serializers.save()
            token=get_tokens_for_user(emp)
            return Response({'token': token, 'data':serializers.data}, status=status.HTTP_201_CREATED)
        return Response(serializers.errors,status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password') 
        user = authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed('User not found')
        serializer = UserSerializer(user)

        return Response({'token': get_tokens_for_user(user), 'data':serializer.data,"message": f"Welcome {user.name}, you have logged in successfully!"}, status=status.HTTP_200_OK)
    
def quiz_attempt(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    questions = Question.objects.filter(quiz=quiz)
    return render(request, 'quiz_attempt.html', {'quiz': quiz, 'questions': questions})


class QuizListView(APIView):
    permission_classes = []  # or [IsAuthenticated] if you want to protect it

    def get(self, request):
        quizzes = Quiz.objects.all()
        serializer = QuizSerializes(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class QuestionListView(APIView):
    permission_classes = []  # or [IsAuthenticated] if you want to protect it

    def get(self, request, pk):
        questions = Question.objects.filter(quiz_id=pk)
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class AnswerListView(APIView):
    permission_classes = []  # or [IsAuthenticated] if you want to protect it

    def get(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=status.HTTP_404_NOT_FOUND)

        # Filter answers that belong to this quiz
        answers = Answer.objects.filter(question__quiz=quiz)
        serializer = AnswerSerializers(answers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request,pk):
        data = request.data
        serializer = AnswerSerializers(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        answer = Answer.objects.get(id=pk)
        serializer = AnswerSerializers(answer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class QuizeHistoryView(APIView):
    def get(self, request):
        submissions = UserSubmission.objects.all()
        serializer = usersubmissionSerializer(submissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class QuizQuestionsAPIView(APIView):
    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        questions_data = []

        for q in quiz.questions.all():
            options = []
            if q.question_type in ['mcq', 'true_false']:
                for a in q.answers.all():
                    options.append({
                        'id': a.id,
                        'text': a.text
                    })

            questions_data.append({
                'id': q.id,
                'text': q.text,
                'question_type': q.question_type,
                'options': options
            })

        return Response({'questions': questions_data})

class QuizSubmitAPIView(APIView):
    def post(self, request, quiz_id):
        try:
            quiz = get_object_or_404(Quiz, id=quiz_id)
            data = request.data
            user_name = data.get('user_name')
            answers = data.get('answers', {})

            if not user_name:
                return Response({'error': 'User name is required'}, status=status.HTTP_400_BAD_REQUEST)

            submission = UserSubmission.objects.create(quiz=quiz, user_name=user_name)
            total_questions = quiz.questions.count()
            correct_count = 0
            results = []

            for question_id, answer_value in answers.items():
                try:
                    question = Question.objects.get(id=question_id)
                except Question.DoesNotExist:
                    continue

                is_correct = False
                selected_answer = None
                selected_text = str(answer_value).strip()

                if question.question_type in ['mcq', 'true_false']:
                    try:
                        selected_answer = Answer.objects.get(id=int(answer_value))
                        selected_text = selected_answer.text
                        is_correct = selected_answer.is_correct
                    except (Answer.DoesNotExist, ValueError, TypeError):
                        is_correct = False
                else:  # short answer
                    correct_answer = Answer.objects.filter(question=question, is_correct=True).first()
                    if correct_answer and selected_text.lower() == correct_answer.text.strip().lower():
                        is_correct = True
                    selected_answer = None

                UserAnswer.objects.create(
                    submission=submission,
                    question=question,
                    answer=selected_answer,
                    is_correct=is_correct
                )

                if is_correct:
                    correct_count += 1

                results.append({
                    "question_id": question.id,
                    "selected_answer": selected_text,
                    "is_correct": is_correct
                })

            submission.score = correct_count
            submission.save()

            return Response({
                "user_name": user_name,
                "score": correct_count,
                "total_questions": total_questions,
                "results": results
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Catch-all to ensure DRF always gets a Response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AddquestionAPIView(APIView):
    def post(self, request):
        data = request.data
        serializer = QuestionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EventListView(APIView):
    permission_classes = []  # or [IsAuthenticated] if you want to protect it

    def get(self, request):
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)