from django.conf import settings
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from ...models import DOCUMENT_CLASSIFICATION
from .utils import make_project, make_tag, make_user, remove_all_role_mappings


class TestTagList(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.project = make_project(
            task=DOCUMENT_CLASSIFICATION,
            users=['annotator'],
            roles=[settings.ROLE_ANNOTATOR]
        )
        cls.non_member = make_user(username='bob')
        make_tag(project=cls.project.item)
        cls.url = reverse(viewname='tag_list', args=[cls.project.item.id])

    def test_return_tags_to_member(self):
        self.client.force_login(self.project.users[0])
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_does_not_return_tags_to_non_member(self):
        self.client.force_login(self.non_member)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_does_not_return_tags_to_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @classmethod
    def doCleanups(cls):
        remove_all_role_mappings()


class TestTagCreate(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.project = make_project(
            task=DOCUMENT_CLASSIFICATION,
            users=['admin', 'approver', 'annotator'],
            roles=[
                settings.ROLE_PROJECT_ADMIN,
                settings.ROLE_ANNOTATION_APPROVER,
                settings.ROLE_ANNOTATOR,
            ]
        )
        cls.non_member = make_user(username='bob')
        cls.url = reverse(viewname='tag_list', args=[cls.project.item.id])
        cls.data = {'text': 'example'}

    def test_allow_admin_to_create_tag(self):
        self.client.force_login(self.project.users[0])
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['text'], self.data['text'])

    def test_disallow_non_admin_to_create_tag(self):
        for member in self.project.users[1:]:
            self.client.force_login(member)
            response = self.client.post(self.url, data=self.data)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_disallow_unauthenticated_user_to_create_tag(self):
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @classmethod
    def doCleanups(cls):
        remove_all_role_mappings()


class TestTagDelete(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.project = make_project(
            task=DOCUMENT_CLASSIFICATION,
            users=['admin', 'approver', 'annotator'],
            roles=[
                settings.ROLE_PROJECT_ADMIN,
                settings.ROLE_ANNOTATION_APPROVER,
                settings.ROLE_ANNOTATOR,
            ]
        )
        cls.non_member = make_user(username='bob')

    def setUp(self):
        tag = make_tag(project=self.project.item)
        self.url = reverse(viewname='tag_detail', args=[self.project.item.id, tag.id])

    def test_allow_admin_to_delete_tag(self):
        self.client.force_login(self.project.users[0])
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_disallow_non_admin_to_delete_tag(self):
        for member in self.project.users[1:]:
            self.client.force_login(member)
            response = self.client.delete(self.url)
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_disallow_unauthenticated_user_to_delete_tag(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @classmethod
    def doCleanups(cls):
        remove_all_role_mappings()