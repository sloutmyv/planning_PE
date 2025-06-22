from django.core.management.base import BaseCommand
from core.models import Function
import random


class Command(BaseCommand):
    help = 'Create test functions for development'

    def handle(self, *args, **options):
        # Function names for different categories
        technical_functions = [
            "Développeur Frontend", "Développeur Backend", "DevOps Engineer", 
            "Architecte Solution", "Administrateur Système", "Analyste Sécurité",
            "Ingénieur Réseau", "Technicien Support", "Database Administrator",
            "Quality Assurance Engineer"
        ]
        
        management_functions = [
            "Chef de Projet", "Directeur Technique", "Product Owner", 
            "Scrum Master", "Responsable Équipe", "Directeur Général",
            "Directeur Commercial", "Responsable RH", "Contrôleur de Gestion",
            "Responsable Marketing"
        ]
        
        operational_functions = [
            "Secrétaire Administrative", "Comptable", "Assistant RH",
            "Réceptionniste", "Agent d'Accueil", "Coordinateur Logistique",
            "Responsable Maintenance", "Gestionnaire Paie", "Assistant Commercial",
            "Chargé de Communication"
        ]
        
        # Descriptions corresponding to functions
        descriptions = {
            "Développeur Frontend": "Développement d'interfaces utilisateur modernes et responsive avec React, Vue.js ou Angular",
            "Développeur Backend": "Développement d'APIs REST et services backend avec Python, Java ou Node.js",
            "DevOps Engineer": "Gestion de l'infrastructure cloud, CI/CD, containerisation avec Docker et Kubernetes",
            "Architecte Solution": "Conception d'architectures logicielles évolutives et sécurisées",
            "Administrateur Système": "Administration des serveurs Linux/Windows, gestion des accès et sauvegardes",
            "Analyste Sécurité": "Audit de sécurité, tests de pénétration et mise en place de politiques de sécurité",
            "Ingénieur Réseau": "Configuration et maintenance des équipements réseau, monitoring et optimisation",
            "Technicien Support": "Support technique niveau 1 et 2, résolution d'incidents utilisateurs",
            "Database Administrator": "Administration des bases de données, optimisation des performances et sauvegardes",
            "Quality Assurance Engineer": "Tests fonctionnels et automatisés, validation de la qualité logicielle",
            "Chef de Projet": "Pilotage de projets informatiques, coordination d'équipes et respect des délais",
            "Directeur Technique": "Direction technique, stratégie technologique et encadrement d'équipes",
            "Product Owner": "Définition des besoins produit, priorisation du backlog et interface client",
            "Scrum Master": "Animation des cérémonies Scrum, facilitation d'équipe et amélioration continue",
            "Responsable Équipe": "Management d'équipe, entretiens individuels et développement des compétences",
            "Directeur Général": "Direction générale de l'entreprise, stratégie globale et représentation externe",
            "Directeur Commercial": "Développement commercial, négociation contrats et gestion du chiffre d'affaires",
            "Responsable RH": "Gestion des ressources humaines, recrutement et formation des collaborateurs",
            "Contrôleur de Gestion": "Analyse financière, reporting et contrôle budgétaire",
            "Responsable Marketing": "Stratégie marketing, communication digitale et développement de la marque",
            "Secrétaire Administrative": "Gestion administrative, accueil téléphonique et organisation des plannings",
            "Comptable": "Tenue de la comptabilité, déclarations fiscales et rapprochements bancaires",
            "Assistant RH": "Support RH, gestion administrative du personnel et suivi des formations",
            "Réceptionniste": "Accueil physique et téléphonique, gestion du courrier et des visiteurs",
            "Agent d'Accueil": "Premier contact client, orientation visiteurs et gestion des badges d'accès",
            "Coordinateur Logistique": "Coordination des livraisons, gestion des stocks et suivi des commandes",
            "Responsable Maintenance": "Maintenance préventive et curative, gestion des prestataires techniques",
            "Gestionnaire Paie": "Établissement des bulletins de paie, déclarations sociales et suivi des congés",
            "Assistant Commercial": "Support commercial, préparation des devis et suivi de la relation client",
            "Chargé de Communication": "Communication interne et externe, animation des réseaux sociaux"
        }
        
        all_functions = technical_functions + management_functions + operational_functions
        
        # Clear existing test functions (optional - comment this line if you want to keep existing data)
        Function.objects.filter(designation__in=all_functions).delete()
        
        created_count = 0
        
        for function_name in all_functions:
            # 20% chance of being inactive
            is_active = random.random() > 0.2
            
            function = Function.objects.create(
                designation=function_name,
                description=descriptions.get(function_name, ""),
                status=is_active
            )
            
            created_count += 1
            
            status_text = "Active" if is_active else "Inactive"
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created function: {function.designation} ({status_text})'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {created_count} test functions:'
            )
        )
        self.stdout.write(f'- Technical functions: {len(technical_functions)}')
        self.stdout.write(f'- Management functions: {len(management_functions)}') 
        self.stdout.write(f'- Operational functions: {len(operational_functions)}')
        
        active_count = Function.objects.filter(status=True).count()
        inactive_count = Function.objects.filter(status=False).count()
        self.stdout.write(f'- Active: {active_count}')
        self.stdout.write(f'- Inactive: {inactive_count}')