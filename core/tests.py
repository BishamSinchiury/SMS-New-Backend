import json
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from core.factories import FactoryHelper
from Users.models import Person, Student, CustomUser
from academics.services import AdmissionService

class TenantIsolationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.org1 = FactoryHelper.create_org(name="Org 1")
        self.org2 = FactoryHelper.create_org(name="Org 2")
        
        self.user1 = FactoryHelper.create_user("u1@test.com")
        self.person1 = FactoryHelper.create_person(self.org1, user=self.user1, first_name="U1")
        
        self.user2 = FactoryHelper.create_user("u2@test.com")
        self.person2 = FactoryHelper.create_person(self.org2, user=self.user2, first_name="U2")

        # Create data in Org 2
        FactoryHelper.create_person(self.org2, first_name="Target")

    def test_user_cannot_see_other_org_data(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('person-list'))
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should only see self (U1), not U2 or Target from Org 2
        self.assertEqual(response.data['count'], 1) 
        self.assertEqual(response.data['results'][0]['first_name'], "U1")

class AtomicAdmissionTest(TestCase):
    def setUp(self):
        self.org = FactoryHelper.create_org()
        self.person = FactoryHelper.create_person(self.org)
        self.year = FactoryHelper.create_academic_year(self.org)
        self.class_sec = FactoryHelper.create_class_section(self.org)

    def test_admission_success(self):
        AdmissionService.admit_student(
            self.org, self.person, self.year.id, self.class_sec.id, "ADM001"
        )
        self.assertTrue(Student.objects.filter(person=self.person).exists())
        self.assertEqual(self.person.student_profile.current_status, 'ACTIVE')

    def test_admission_duplicate_fail(self):
        # 1st Admission
        AdmissionService.admit_student(
            self.org, self.person, self.year.id, self.class_sec.id, "ADM001"
        )
        
        # 2nd Admission (Should fail integrity)
        with self.assertRaises(Exception):
             AdmissionService.admit_student(
                self.org, self.person, self.year.id, self.class_sec.id, "ADM001"
            )
