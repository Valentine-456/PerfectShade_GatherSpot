from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from PerfectSpot.models import Event

CustomUser = get_user_model()


class AuthTestCase(APITestCase):
    def setUp(self):
        """
        Runs before every test. You can create any test data here if needed.
        """
        self.register_url = reverse('signup')  # matches the name in urls.py
        self.login_url = reverse('signin')  # matches the name in urls.py

    def test_register_success(self):
        """
        Test successful registration of a new user.
        """
        data = {
            "username": "testuser",
            "password": "testpass123",
            "email": "test@example.com",
            "user_type": "individual"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], "User registered successfully.")
        self.assertIn('data', response.data)
        self.assertIn('token', response.data['data'])
        self.assertEqual(response.data['data']['username'], "testuser")

        # Check that the user actually exists in the database
        user_exists = CustomUser.objects.filter(username="testuser").exists()
        self.assertTrue(user_exists)

    def test_register_fail_missing_fields(self):
        """
        Test registration failing due to missing required fields.
        """
        data = {
            # Omitting username and email on purpose
            "password": "testpass123",
            "user_type": "individual"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertFalse(response.data['success'])
        self.assertIn('data', response.data)
        self.assertIn('username', response.data['data'])  # e.g., "This field is required."
        self.assertIn('email', response.data['data'])  # e.g., "This field is required."

    def test_register_fail_duplicate_username(self):
        """
        Test registration failing when a user tries to register with a username that already exists.
        """
        # First user
        CustomUser.objects.create_user(username="testuser", email="test@example.com", password="testpass123")

        # Second attempt with same username
        data = {
            "username": "testuser",
            "password": "anotherpass",
            "email": "another@example.com",
            "user_type": "individual"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertFalse(response.data['success'])
        # The exact error might differ based on how your serializer handles duplicates

    def test_login_success(self):
        """
        Test successful login with valid credentials.
        """
        # Create a user in the DB
        user = CustomUser.objects.create_user(username="loginuser", email="login@example.com", password="mypass")

        data = {
            "username": "loginuser",
            "password": "mypass"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], "Logged in successfully.")
        self.assertIn('token', response.data['data'])
        self.assertEqual(response.data['data']['username'], "loginuser")
        self.assertEqual(response.data['data']['userID'], user.id)

    def test_login_fail_invalid_credentials(self):
        """
        Test that login fails when credentials are invalid.
        """
        # Create a user in the DB
        CustomUser.objects.create_user(username="someuser", password="somepass")

        data = {
            "username": "someuser",
            "password": "wrongpass"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertFalse(response.data['success'])
        self.assertIn("Invalid credentials.", response.data['data']['non_field_errors'])


class EventTestCase(APITestCase):
    def setUp(self):
        # Create test user
        self.user = CustomUser.objects.create_user(
            username='tester', email='tester@example.com', password='123456'
        )
        # Store the create-event URL
        self.create_url = reverse('create_event')
        # Also store the login URL, so we can get a token
        self.login_url = reverse('signin')

    def _login_and_get_token(self, username, password):
        """Helper method to sign in with username/password and return JWT token."""
        response = self.client.post(self.login_url, {
            "username": username,
            "password": password
        }, format='json')
        # The test expects a token at response.data['data']['token'] – adapt if needed
        return response.data['data']['token']

    def test_create_event_success(self):
        # 1. Get a token
        token = self._login_and_get_token("tester", "123456")
        # 2. Set the Authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # 3. Now do the POST request to create an event
        data = {
            "title": "Test Event",
            "description": "Test Description",
            "location": "Test Location",
            "date": "2025-06-15T14:00:00Z",
            "is_promoted": False
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(response.data['success'])

        event_id = response.data['data']['id']
        event_exists = Event.objects.filter(pk=event_id, creator=self.user).exists()
        self.assertTrue(event_exists)

    def test_delete_event(self):
        # Create an event in DB
        token = self._login_and_get_token("tester", "123456")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        event = Event.objects.create(
            title="Delete Me",
            description="Desc",
            location="Place",
            date="2025-06-15T14:00:00Z",
            creator=self.user
        )
        delete_url = f'/api/events/{event.id}'
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertFalse(Event.objects.filter(pk=event.id).exists())
