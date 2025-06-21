import pytest
from datetime import date
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
            grade="Agent",
            hire_date=date(2023, 1, 15)
        )
        assert agent.matricule == "A1234"
        assert agent.first_name == "Jean"
        assert agent.last_name == "Dupont"
        assert agent.grade == "Agent"
        assert agent.hire_date == date(2023, 1, 15)
        assert agent.departure_date is None
        assert str(agent) == "A1234 - Jean Dupont"
    
    def test_matricule_validation_valid_format(self):
        """Test matricule validation with valid format"""
        valid_matricules = ["A1234", "B5678", "Z9999"]
        for matricule in valid_matricules:
            agent = Agent(
                matricule=matricule,
                first_name="Test",
                last_name="User",
                grade="Agent",
                hire_date=date(2023, 1, 1)
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
                grade="Agent",
                hire_date=date(2023, 1, 1)
            )
            with pytest.raises(ValidationError):
                agent.full_clean()
    
    def test_matricule_unique_constraint(self):
        """Test that matricule must be unique"""
        Agent.objects.create(
            matricule="A1234",
            first_name="Jean",
            last_name="Dupont",
            grade="Agent",
            hire_date=date(2023, 1, 15)
        )
        
        with pytest.raises(IntegrityError):
            Agent.objects.create(
                matricule="A1234",
                first_name="Marie",
                last_name="Martin",
                grade="Cadre",
                hire_date=date(2023, 2, 1)
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
                grade=grade,
                hire_date=date(2023, 1, 1)
            )
            agent.full_clean()
    
    def test_string_representation(self):
        """Test the string representation of Agent model"""
        agent = Agent(
            matricule="B5678",
            first_name="Marie",
            last_name="Martin",
            grade="Maitrise",
            hire_date=date(2023, 1, 1)
        )
        assert str(agent) == "B5678 - Marie Martin"
    
    def test_model_meta_attributes(self):
        """Test model meta attributes"""
        assert Agent._meta.verbose_name == "Agent"
        assert Agent._meta.verbose_name_plural == "Agents"
    
    def test_hire_date_has_default(self):
        """Test that hire_date has a default value"""
        agent = Agent(
            matricule="D1234",
            first_name="Test",
            last_name="User",
            grade="Agent"
            # hire_date will use default value
        )
        agent.full_clean()  # Should not raise ValidationError
        assert agent.hire_date is not None
    
    def test_departure_date_optional(self):
        """Test that departure_date is optional"""
        agent = Agent(
            matricule="E1234",
            first_name="Test",
            last_name="User",
            grade="Agent",
            hire_date=date(2023, 1, 1)
            # departure_date is optional
        )
        agent.full_clean()  # Should not raise ValidationError
    
    def test_agent_with_departure_date(self):
        """Test creating an agent with departure date"""
        agent = Agent.objects.create(
            matricule="F1234",
            first_name="Pierre",
            last_name="Durand",
            grade="Cadre",
            hire_date=date(2020, 6, 1),
            departure_date=date(2023, 12, 31)
        )
        assert agent.hire_date == date(2020, 6, 1)
        assert agent.departure_date == date(2023, 12, 31)
    
    def test_departure_date_must_be_after_hire_date(self):
        """Test that departure date must be after hire date"""
        agent = Agent(
            matricule="G1234",
            first_name="Test",
            last_name="User",
            grade="Agent",
            hire_date=date(2023, 6, 1),
            departure_date=date(2023, 5, 1)  # Before hire date
        )
        with pytest.raises(ValidationError) as exc_info:
            agent.full_clean()
        assert 'departure_date' in exc_info.value.message_dict
    
    def test_departure_date_equal_to_hire_date_invalid(self):
        """Test that departure date cannot be equal to hire date"""
        agent = Agent(
            matricule="H1234",
            first_name="Test",
            last_name="User",
            grade="Agent",
            hire_date=date(2023, 6, 1),
            departure_date=date(2023, 6, 1)  # Same as hire date
        )
        with pytest.raises(ValidationError) as exc_info:
            agent.full_clean()
        assert 'departure_date' in exc_info.value.message_dict
    
    def test_valid_departure_date_after_hire_date(self):
        """Test that departure date after hire date is valid"""
        agent = Agent(
            matricule="I1234",
            first_name="Test",
            last_name="User",
            grade="Agent",
            hire_date=date(2023, 6, 1),
            departure_date=date(2023, 6, 2)  # After hire date
        )
        agent.full_clean()  # Should not raise ValidationError