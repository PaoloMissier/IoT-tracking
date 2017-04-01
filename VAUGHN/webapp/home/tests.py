
from django.test import TestCase
from .models import Cubes
import datetime
from rest_framework.test import APIClient
from rest_framework import status
from django.core.urlresolvers import reverse


class ModelTestCase(TestCase):

    def setUp(self):
        """Define the test client and other test variables."""
        self.Cubes_prodid = "prodID"
        self.Cubes_consid = "consID"
        self.Cubes_topic = "topic"
        self.Cubes_timestamp = datetime.datetime.now()
        self.Cubes_cnt = 0
        self.cubes = Cubes(prodID=self.Cubes_prodid,
                           consID=self.Cubes_consid,
                           topic=self.Cubes_topic,
                           timestamp=self.Cubes_timestamp,
                           cnt=self.Cubes_cnt)

    def test_model_can_create_a_bucketlist(self):
        old_count = Cubes.objects.count()
        self.cubes.save()
        new_count = Cubes.objects.count()
        self.assertNotEqual(old_count, new_count)


class ViewTestCase(TestCase):
    """Test suite for the api views."""

    def setUp(self):
        """Define the test client and other test variables."""
        self.client = APIClient()
        self.cubes_data = {'prodID': 'prod',
                           'consid': 'cons',
                           'topic': 'topic',
                           'cnt': '123',
                           'timestamp':datetime.datetime.now()}
        self.response = self.client.post(
            reverse('create'),
            self.cubes_data,
            format="json")

    def test_api_can_create_a_bucketlist(self):
        """Test the api has bucket creation capability."""
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
