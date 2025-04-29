from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from PerfectSpot.models import Event, Review

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

        # create an organization user
        self.org_user = CustomUser.objects.create_user(
            username='org', email='org@example.com', password='orgpass', user_type='organization'
        )

        # Store the create-event URL
        self.create_url = reverse('create_event')
        # Also store the login URL, so we can get a token
        self.login_url = reverse('signin')
        self.promote_url = lambda pk: reverse('rsvp-event').replace('rsvp', 'promote').rsplit('/', 1)[
                                          0] + f'{pk}/promote/'

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

    def test_edit_event(self):
        token = self._login_and_get_token("tester", "123456")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # First, create an event
        create = self.client.post(
            reverse('create_event'),
            {"title": "Orig", "description": "D", "location": "L",
             "date": "2025-06-15T14:00:00Z", "is_promoted": False},
            format='json'
        )
        eid = create.data['data']['id']

        # Now edit just the title & date
        patch = self.client.patch(
            f'/api/events/{eid}/edit/',
            {"title": "Updated", "date": "2025-07-01T10:00:00Z"},
            format='json'
        )
        self.assertEqual(patch.status_code, status.HTTP_200_OK)
        self.assertTrue(patch.data['success'])
        self.assertEqual(patch.data['data']['title'], "Updated")
        self.assertEqual(patch.data['data']['date'], "2025-07-01T10:00:00Z")

    def _create_event_as(self, username, password):
        token = self._login_and_get_token(username, password)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        resp = self.client.post(self.create_url, {
            "title": "Promo Test",
            "description": "Testing promotion",
            "location": "Test Location",
            "date": "2025-08-01T12:00:00Z",
            "is_promoted": False
        }, format='json')
        return resp.data['data']['id']

    def test_promote_event_success(self):
        # Org user creates the event
        event_id = self._create_event_as('org', 'orgpass')

        # Org user promotes it
        url = f'/api/events/{event_id}/promote/'
        response = self.client.patch(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['eventID'], event_id)
        self.assertTrue




class ReviewTestCase(APITestCase):
    def setUp(self):
        # URLs
        self.login_url  = reverse('signin')
        self.create_url = reverse('create_event')

        # 1) Create a reviewer user
        self.reviewer = CustomUser.objects.create_user(
            username='reviewer',
            email='reviewer@example.com',
            password='reviewpass',
            user_type='individual'
        )

        # 2) Log them in & set JWT auth header
        login_resp = self.client.post(
            self.login_url,
            {'username': 'reviewer', 'password': 'reviewpass'},
            format='json'
        )
        token = login_resp.data['data']['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # 3) Create an event they can review
        create_resp = self.client.post(
            self.create_url,
            {
                'title': 'ReviewEvent',
                'description': 'For review tests',
                'location': 'Loc',
                'date': '2025-09-01T12:00:00Z',
                'is_promoted': False
            },
            format='json'
        )
        self.event_id = create_resp.data['data']['id']


    def test_list_reviews_empty(self):
        """GET /events/{id}/reviews/ should return empty list when no reviews."""
        url = reverse('list_reviews', args=[self.event_id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data, [])


    def test_add_review(self):
        """POST /events/{id}/reviews/add should create a new review."""
        url = reverse('add_review', args=[self.event_id])
        payload = {'rating': 5, 'comment': 'Excellent!'}
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Payload returned by the serializer:
        self.assertIn('id', resp.data)
        self.assertEqual(resp.data['rating'], 5)
        self.assertEqual(resp.data['comment'], 'Excellent!')
        self.assertEqual(resp.data['reviewer'], 'reviewer')
        # And a Review object really exists in the DB:
        self.assertTrue(
            Review.objects.filter(
                event_id=self.event_id,
                reviewer=self.reviewer,
                rating=5,
                comment='Excellent!'
            ).exists()
        )


    def test_edit_review_success(self):
        """PATCH /events/{id}/reviews/{rid} should let the author update their review."""
        # first create one
        add_url = reverse('add_review', args=[self.event_id])
        add_resp = self.client.post(add_url, {'rating':4, 'comment':'Good'}, format='json')
        review_id = add_resp.data['id']

        edit_url = reverse('edit_review', args=[self.event_id, review_id])
        patch_resp = self.client.patch(edit_url,
                                      {'rating':3, 'comment':'Okay'},
                                      format='json')
        self.assertEqual(patch_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_resp.data['rating'], 3)
        self.assertEqual(patch_resp.data['comment'], 'Okay')


    def test_edit_review_forbidden(self):
        """A different user should not be able to patch someone else’s review."""
        # create review as reviewer
        add_url = reverse('add_review', args=[self.event_id])
        add_resp = self.client.post(add_url, {'rating':4, 'comment':'Good'}, format='json')
        review_id = add_resp.data['id']

        # create & login as another user
        other = CustomUser.objects.create_user(
            username='other',
            email='other@example.com',
            password='otherpass',
            user_type='individual'
        )
        other_login = self.client.post(
            self.login_url,
            {'username': 'other', 'password': 'otherpass'},
            format='json'
        )
        other_token = other_login.data['data']['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {other_token}')

        # attempt to edit – should 404 (not in their queryset)
        edit_url = reverse('edit_review', args=[self.event_id, review_id])
        resp = self.client.patch(edit_url, {'rating':1}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)


    def test_delete_review(self):
        """DELETE /events/{id}/reviews/{rid}/delete should remove the review."""
        # create a review
        add_url = reverse('add_review', args=[self.event_id])
        add_resp = self.client.post(add_url, {'rating':2, 'comment':'Bad'}, format='json')
        review_id = add_resp.data['id']

        del_url = reverse('delete_review', args=[self.event_id, review_id])
        resp = self.client.delete(del_url)
        # Generic DestroyAPIView returns 204 No Content
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Review.objects.filter(pk=review_id).exists())

