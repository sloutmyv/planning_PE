import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from core.models import Agent


@pytest.mark.django_db
class TestAgentModel:
    
    def test_create_agent_valid_data(self):
        """Test creating an agent with valid data"""
        agent = Agent.objects.create(
            matricule="A1234",
            first_name="Jean",
            last_name="Dupont",
            grade="Agent"
        )
        assert agent.matricule == "A1234"
        assert agent.first_name == "Jean"
        assert agent.last_name == "Dupont"
        assert agent.grade == "Agent"
        assert str(agent) == "A1234 - Jean Dupont"
    
    def test_matricule_validation_valid_format(self):
        """Test matricule validation with valid format"""
        valid_matricules = ["A1234", "B5678", "Z9999"]
        for matricule in valid_matricules:
            agent = Agent(
                matricule=matricule,
                first_name="Test",
                last_name="User",
                grade="Agent"
            )
            agent.full_clean()  # This will raise ValidationError if invalid
    
    def test_matricule_validation_invalid_format(self):
        """Test matricule validation with invalid formats"""
        invalid_matricules = ["1234A", "AB123", "A123", "A12345", "a1234", ""]
        for matricule in invalid_matricules:
            agent = Agent(
                matricule=matricule,
                first_name="Test",
                last_name="User",
                grade="Agent"
            )
            with pytest.raises(ValidationError):
                agent.full_clean()
    
    def test_matricule_unique_constraint(self):
        """Test that matricule must be unique"""
        Agent.objects.create(
            matricule="A1234",
            first_name="Jean",
            last_name="Dupont",
            grade="Agent"
        )
        
        with pytest.raises(IntegrityError):
            Agent.objects.create(
                matricule="A1234",
                first_name="Marie",
                last_name="Martin",
                grade="Cadre"
            )
    
    def test_grade_choices(self):
        """Test that only valid grade choices are accepted"""
        valid_grades = ["Agent", "Maitrise", "Cadre"]
        matricules = ["A1234", "B5678", "C9999"]
        for i, grade in enumerate(valid_grades):
            agent = Agent(
                matricule=matricules[i],
                first_name="Test",
                last_name="User",
                grade=grade
            )
            agent.full_clean()
    
    def test_string_representation(self):
        """Test the string representation of Agent model"""
        agent = Agent(
            matricule="B5678",
            first_name="Marie",
            last_name="Martin",
            grade="Maitrise"
        )
        assert str(agent) == "B5678 - Marie Martin"
    
    def test_model_meta_attributes(self):
        """Test model meta attributes"""
        assert Agent._meta.verbose_name == "Agent"
        assert Agent._meta.verbose_name_plural == "Agents"