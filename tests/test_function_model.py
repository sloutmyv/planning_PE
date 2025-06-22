import pytest
from core.models import Function


@pytest.mark.django_db
class TestFunctionModel:
    
    def test_create_function_with_required_fields(self):
        """Test creating a function with only required fields"""
        function = Function.objects.create(
            designation="Développeur Web"
        )
        assert function.designation == "Développeur Web"
        assert function.description is None
        assert function.status is True  # Default value
        assert str(function) == "Développeur Web"
    
    def test_create_function_with_all_fields(self):
        """Test creating a function with all fields"""
        function = Function.objects.create(
            designation="Chef de Projet",
            description="Responsable de la gestion des projets informatiques",
            status=True
        )
        assert function.designation == "Chef de Projet"
        assert function.description == "Responsable de la gestion des projets informatiques"
        assert function.status is True
        assert str(function) == "Chef de Projet"
    
    def test_function_with_inactive_status(self):
        """Test creating a function with inactive status"""
        function = Function.objects.create(
            designation="Fonction Obsolète",
            description="Une fonction qui n'est plus utilisée",
            status=False
        )
        assert function.designation == "Fonction Obsolète"
        assert function.description == "Une fonction qui n'est plus utilisée"
        assert function.status is False
    
    def test_function_description_optional(self):
        """Test that description field is optional"""
        function = Function(
            designation="Testeur"
            # description is not provided
        )
        function.full_clean()  # Should not raise ValidationError
        function.save()
        assert function.description is None
    
    def test_function_status_default_true(self):
        """Test that status field defaults to True"""
        function = Function(
            designation="Analyste"
        )
        assert function.status is True
    
    def test_string_representation(self):
        """Test the string representation of Function model"""
        function = Function(
            designation="Architecte Logiciel",
            description="Conception de l'architecture des applications"
        )
        assert str(function) == "Architecte Logiciel"
    
    def test_model_meta_attributes(self):
        """Test model meta attributes"""
        assert Function._meta.verbose_name == "Fonction"
        assert Function._meta.verbose_name_plural == "Fonctions"
    
    def test_designation_max_length(self):
        """Test that designation field has proper max length"""
        long_designation = "A" * 200
        function = Function(
            designation=long_designation
        )
        function.full_clean()  # Should not raise ValidationError
        
        # Test with exceeding max length
        too_long_designation = "A" * 201
        function_too_long = Function(
            designation=too_long_designation
        )
        with pytest.raises(Exception):  # ValidationError or similar
            function_too_long.full_clean()
    
    def test_multiple_functions_can_exist(self):
        """Test creating multiple functions"""
        Function.objects.create(designation="Développeur Frontend")
        Function.objects.create(designation="Développeur Backend")
        Function.objects.create(designation="DevOps Engineer")
        
        assert Function.objects.count() == 3
        
        # Test that designations can be the same (no unique constraint)
        Function.objects.create(designation="Développeur Frontend")
        assert Function.objects.count() == 4