from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from .forms import CustomPasswordChangeForm, EmailChangeForm, ProfileEditForm, UserLogInForm, UserRegistrationForm
from .models import Audio, LanguageLevel, Lesson, Profile, Task, UserTasksProgress
from .views import check_level_completion

User = get_user_model()


class AuthViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', password='testpass123', email='test@example.com')
        self.profile = Profile.objects.create(user=self.user)
        self.language_level = LanguageLevel.objects.create(level='A1')
        self.lesson = Lesson.objects.create(language_level=self.language_level, lesson_number=1, title='Test Lesson')
        self.task = Task.objects.create(
            lesson=self.lesson,
            question='Test Question',
            correct_answer='2',
            option1='Option1',
            option2='Option2',
            option3='Option3',
        )

    def test_main_page_view(self):
        response = self.client.get(reverse('main_page'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'html/pages/main_page.html')

    def test_policy_view(self):
        response = self.client.get(reverse('private_policy'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'html/pages/policy_page.html')

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'html/pages/login_page.html')
        self.assertIsInstance(response.context['form'], UserLogInForm)

    def test_login_view_post_success(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'testpass123'})
        self.assertRedirects(response, reverse('main_page'))

    def test_login_view_post_failure(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Invalid username or password')

    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'html/pages/registry_page.html')
        self.assertIsInstance(response.context['form'], UserRegistrationForm)

    def test_register_view_post_success(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newuser',
                'email': 'new@example.com',
                'password1': 'complexpass123',
                'password2': 'complexpass123',
            },
        )
        self.assertRedirects(response, reverse('main_page'))
        self.assertTrue(User.objects.filter(username='newuser').exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Registration is successful!')

    def test_register_view_post_failure(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newuser',
                'email': 'invalid-email',
                'password1': 'complexpass123',
                'password2': 'differentpass',
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['form'].is_valid())


class AuthenticatedViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123', email='test@example.com')
        self.profile = Profile.objects.create(user=self.user)
        self.language_level = LanguageLevel.objects.create(level='A1')
        self.lesson = Lesson.objects.create(language_level=self.language_level, lesson_number=1, title='Test Lesson')
        self.task = Task.objects.create(
            lesson=self.lesson,
            question='Test Question',
            correct_answer='1',
            option1='Option1',
            option2='Option2',
            option3='Option3',
        )
        self.client.login(username='testuser', password='testpass123')

    def test_profile_view(self):
        response = self.client.get(reverse('profile_view'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'html/pages/account_page.html')
        self.assertEqual(response.context['user'], self.user)
        self.assertEqual(response.context['profile'], self.profile)

    def test_langlevel_view(self):
        response = self.client.get(reverse('langlevel'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'html/pages/langlevel_page.html')
        self.assertEqual(len(response.context['levels_data']), 1)
        self.assertEqual(response.context['levels_data'][0]['level'], self.language_level)

    def test_lessons_view(self):
        response = self.client.get(reverse('lessons', kwargs={'level': 'A1'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'html/pages/lessons_page.html')
        self.assertEqual(response.context['level'], 'A1')
        self.assertEqual(len(response.context['lessons_data']), 1)
        self.assertEqual(response.context['lessons_data'][0]['lesson'], self.lesson)

    def test_tasks_view_get(self):
        response = self.client.get(reverse('tasks', kwargs={'level': 'A1', 'lesson': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'html/pages/tasks_page.html')
        self.assertEqual(len(response.context['tasks']), 1)
        self.assertEqual(response.context['tasks'][0], self.task)

    def test_tasks_view_post_failure(self):
        response = self.client.post(reverse('tasks', kwargs={'level': 'A1', 'lesson': 1}), {'answer_1': '3'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['show_answers'])
        self.assertEqual(response.context['score'], 0)

    def test_tasks_view_already_completed(self):
        UserTasksProgress.objects.create(user=self.user, level='A1', lesson=1, result=100)
        response = self.client.get(reverse('tasks', kwargs={'level': 'A1', 'lesson': 1}))
        self.assertRedirects(response, reverse('lessons', kwargs={'level': 'A1'}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'You have already passed this lesson 100%!!')

    def test_edit_profile_view_get(self):
        response = self.client.get(reverse('edit_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'html/pages/accountedit_page.html')
        self.assertIsInstance(response.context['profile_form'], ProfileEditForm)
        self.assertIsInstance(response.context['email_form'], EmailChangeForm)
        self.assertIsInstance(response.context['password_form'], CustomPasswordChangeForm)

    def test_edit_profile_view_post_profile(self):
        test_image = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(reverse('edit_profile'), {'profile_picture': test_image, 'profile_submit': ''})
        self.assertRedirects(response, reverse('edit_profile'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Your profile picture has been updated!')

    def test_edit_profile_view_post_email(self):
        response = self.client.post(reverse('edit_profile'), {'email': 'new@example.com', 'email_submit': ''})
        self.assertRedirects(response, reverse('edit_profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'new@example.com')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Your email has been updated!')

    def test_edit_profile_view_post_password(self):
        response = self.client.post(
            reverse('edit_profile'),
            {
                'old_password': 'testpass123',
                'new_password1': 'newcomplexpass123',
                'new_password2': 'newcomplexpass123',
                'password_submit': '',
            },
        )
        self.assertRedirects(response, reverse('edit_profile'))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'Your password has been updated!')

    def test_check_level_completion(self):
        # Initially should be False
        self.assertFalse(check_level_completion(self.user, 'A1'))

        # Create completed progress
        UserTasksProgress.objects.create(user=self.user, level='A1', lesson=1, result=100)
        self.assertTrue(check_level_completion(self.user, 'A1'))


class EdgeCaseTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123', email='test@example.com')
        self.profile = Profile.objects.create(user=self.user)
        self.client.login(username='testuser', password='testpass123')

    def test_nonexistent_lesson_tasks_view(self):
        LanguageLevel.objects.create(level='A1')
        response = self.client.get(reverse('tasks', kwargs={'level': 'A1', 'lesson': 999}))
        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_access(self):
        self.client.logout()
        protected_urls = [
            reverse('profile_view'),
            reverse('langlevel'),
            reverse('lessons', kwargs={'level': 'A1'}),
            reverse('tasks', kwargs={'level': 'A1', 'lesson': 1}),
            reverse('edit_profile'),
        ]

        for url in protected_urls:
            response = self.client.get(url)
            self.assertRedirects(response, f"{reverse('login')}?next={url}")


class AudioModelTest(TestCase):
    def setUp(self):
        self.audio = Audio.objects.create(
            title="Test Audio",
            description="Test description",
            audio_file=SimpleUploadedFile("test.mp3", b"file_content"),
            audio_url="https://example.com/audio.mp3",
        )

    def test_audio_creation(self):
        self.assertEqual(self.audio.title, "Test Audio")
        self.assertEqual(self.audio.description, "Test description")
        self.assertTrue(self.audio.audio_file)
        self.assertEqual(self.audio.audio_url, "https://example.com/audio.mp3")

    def test_audio_str_with_title(self):
        self.assertEqual(str(self.audio), "Test Audio")


class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass123")
        self.profile = Profile.objects.create(
            user=self.user, streak=5, completed_levels=3, language_level="A2", achievements="First lesson, Fast learner"
        )

    def test_profile_creation(self):
        self.assertEqual(self.profile.user.username, "testuser")
        self.assertEqual(self.profile.streak, 5)
        self.assertEqual(self.profile.completed_levels, 3)
        self.assertEqual(self.profile.language_level, "A2")
        self.assertEqual(self.profile.achievements, "First lesson, Fast learner")

    def test_profile_str(self):
        self.assertEqual(str(self.profile), "testuser")

    def test_increment_streak(self):
        self.profile.increment_streak()
        self.assertEqual(self.profile.streak, 6)

    def test_reset_streak(self):
        self.profile.reset_streak()
        self.assertEqual(self.profile.streak, 0)

    def test_complete_level(self):
        self.profile.complete_level()
        self.assertEqual(self.profile.completed_levels, 4)


class LanguageLevelModelTest(TestCase):
    def setUp(self):
        self.level = LanguageLevel.objects.create(level="B1", description="Intermediate level")

    def test_language_level_creation(self):
        self.assertEqual(self.level.level, "B1")
        self.assertEqual(self.level.description, "Intermediate level")

    def test_language_level_str(self):
        self.assertEqual(str(self.level), "B1")

    def test_level_choices(self):
        choices = dict(LanguageLevel.LEVEL_CHOICES)
        self.assertEqual(choices["A1"], "A1")
        self.assertEqual(choices["C2"], "C2")


class LessonModelTest(TestCase):
    def setUp(self):
        self.level = LanguageLevel.objects.create(level="A2")
        self.lesson = Lesson.objects.create(
            language_level=self.level, lesson_number=3, title="Past Tense", description="Learning past tense"
        )

    def test_lesson_creation(self):
        self.assertEqual(self.lesson.language_level.level, "A2")
        self.assertEqual(self.lesson.lesson_number, 3)
        self.assertEqual(self.lesson.title, "Past Tense")
        self.assertEqual(self.lesson.description, "Learning past tense")

    def test_lesson_str(self):
        expected_str = "A2 - Lesson 3: Past Tense"
        self.assertEqual(str(self.lesson), expected_str)


class TaskModelTest(TestCase):
    def setUp(self):
        self.level = LanguageLevel.objects.create(level="B2")
        self.lesson = Lesson.objects.create(language_level=self.level, lesson_number=1, title="Conditionals")
        self.audio = Audio.objects.create(title="Task Audio")
        self.task = Task.objects.create(
            lesson=self.lesson,
            question="What is the correct form?",
            correct_answer="Would have gone",
            option1="Will have gone",
            option2="Would had gone",
            option3="Would have went",
            audio=self.audio,
        )

    def test_task_creation(self):
        self.assertEqual(self.task.lesson.title, "Conditionals")
        self.assertEqual(self.task.question, "What is the correct form?")
        self.assertEqual(self.task.correct_answer, "Would have gone")
        self.assertEqual(self.task.option1, "Will have gone")
        self.assertEqual(self.task.option2, "Would had gone")
        self.assertEqual(self.task.option3, "Would have went")
        self.assertEqual(self.task.audio.title, "Task Audio")

    def test_task_str(self):
        self.assertEqual(str(self.task), "Task for Conditionals")

    def test_task_without_options(self):
        task = Task.objects.create(lesson=self.lesson, question="Simple question", correct_answer="Answer")
        self.assertIsNone(task.option1)
        self.assertIsNone(task.option2)
        self.assertIsNone(task.option3)
        self.assertIsNone(task.audio)


class UserTasksProgressModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="progressuser", password="test123")
        self.progress = UserTasksProgress.objects.create(user=self.user, level="C1", lesson=5, result=85)

    def test_progress_creation(self):
        self.assertEqual(self.progress.user.username, "progressuser")
        self.assertEqual(self.progress.level, "C1")
        self.assertEqual(self.progress.lesson, 5)
        self.assertEqual(self.progress.result, 85)
        self.assertIsNotNone(self.progress.date_completed)

    def test_progress_str(self):
        expected_str = "progressuser - Level C1 - Lesson 5 - Result 85%"
        self.assertEqual(str(self.progress), expected_str)

    def test_unique_together_constraint(self):
        # Should not be able to create duplicate progress record
        with self.assertRaises(Exception):
            UserTasksProgress.objects.create(user=self.user, level="C1", lesson=5, result=90)

    def test_default_values(self):
        progress = UserTasksProgress.objects.create(user=self.user)
        self.assertEqual(progress.level, "A1")
        self.assertEqual(progress.lesson, 1)
        self.assertEqual(progress.result, 0)
