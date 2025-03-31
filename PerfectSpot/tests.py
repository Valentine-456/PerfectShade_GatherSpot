from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class AuthTestCase(APITestCase):
    def setUp(self):
        """
        Runs before every test. You can create any test data here if needed.
        """
        self.register_url = reverse('signup')  # matches the name in urls.py
        self.login_url = reverse('signin')     # matches the name in urls.py

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
        self.assertIn('email', response.data['data'])     # e.g., "This field is required."

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
