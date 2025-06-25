from django.test import TestCase, Client
from django.urls import reverse

class HomePageTest(TestCase):
    """Test to verify the home button exists with correct HTML structure."""
    
    def test_home_button_exists(self):
        """Test that the home page contains a home button/link."""
        # Set up
       client = Client()
        home_url = reverse('home')
        # Make request
        response = client.get(home_url)
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Home')
      