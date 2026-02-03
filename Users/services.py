from django.db import transaction
from django.core.exceptions import ValidationError
from Users.models import CustomUser, Person, Student, Teacher, Staff, Guardian

class PersonService:
    @staticmethod
    @transaction.atomic
    def create_person_with_role(organization, data, role_type=None, role_data=None):
        """
        Creates a Person and optionally a role (Student, Teacher, etc.) atomically.
        """
        # Create Person
        person = Person.objects.create(organization=organization, **data)
        
        if role_type == 'STUDENT' and role_data:
            Student.objects.create(organization=organization, person=person, **role_data)
        elif role_type == 'TEACHER' and role_data:
            Teacher.objects.create(organization=organization, person=person, **role_data)
        # Add other roles as needed
        
        return person

class UserService:
    @staticmethod
    @transaction.atomic
    def create_user_for_person(person, email, password):
        """
        Creates a User and links it to an existing Person.
        """
        if person.user:
             raise ValidationError("Person already has a user account.")
        
        user = CustomUser.objects.create_user(email=email, password=password)
        person.user = user
        person.save()
        return user
