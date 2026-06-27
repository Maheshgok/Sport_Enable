"""
Service for creating and managing user profiles
Consolidates profile creation logic by role
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Import database module - handle both import styles
try:
    import firestore_db as db
except ImportError:
    from api import firestore_db as db


class ProfileService:
    """Service for managing user profiles across different roles"""
    
    PROFILE_CREATORS = {
        'athlete': 'create_athlete_profile',
        'coach': 'create_coach_profile',
        'physiotherapist': 'create_physiotherapist_profile',
        'parent': 'create_parent_guardian_profile'
    }
    
    @staticmethod
    def create_profiles_for_roles(user_id: str, roles: List[str], data: Dict) -> Dict:
        """
        Create all role-specific profiles for a user
        
        Args:
            user_id: User ID
            roles: List of roles
            data: Registration data with role-specific fields
        
        Returns:
            Dictionary of created profiles
        """
        profile_data = {}
        
        for role in roles:
            if role in ProfileService.PROFILE_CREATORS:
                try:
                    profile = ProfileService._create_single_profile(role, user_id, data)
                    profile_data[f'{role}_profile'] = profile
                except Exception as e:
                    logger.error(f"Failed to create {role} profile: {e}", exc_info=True)
                    raise
        
        return profile_data
    
    @staticmethod
    def _create_single_profile(role: str, user_id: str, data: Dict) -> Dict:
        """
        Create a single role-specific profile
        
        Args:
            role: Role name
            user_id: User ID
            data: Registration data
        
        Returns:
            Profile data
        """
        if role == 'athlete':
            athlete_profile = db.create_athlete_profile(
                user_id=user_id,
                sport_id=data['sport_id'],
                sport_name=data.get('sport_name', data['sport_id']),
                position=data.get('position'),
                team=data.get('team'),
                custom_baselines=data.get('custom_baselines')
            )
            return {
                'sport_id': data['sport_id'],
                'position': data.get('position'),
                'team': data.get('team')
            }
        
        elif role == 'coach':
            coach_profile = db.create_coach_profile(
                user_id=user_id,
                specialization=data.get('specialization'),
                years_of_experience=data.get('years_of_experience')
            )
            return {
                'specialization': data.get('specialization'),
                'years_of_experience': data.get('years_of_experience')
            }
        
        elif role == 'physiotherapist':
            physio_profile = db.create_physiotherapist_profile(
                user_id=user_id,
                specialization=data.get('specialization'),
                license_number=data.get('license_number')
            )
            return {
                'license_number': data.get('license_number'),
                'specialization': data.get('specialization')
            }
        
        elif role == 'parent':
            guardian_profile = db.create_parent_guardian_profile(
                user_id=user_id,
                guardian_type=data['guardian_type'],
                relationship_to_athlete=data.get('relationship_to_athlete'),
                permissions=data.get('permissions')
            )
            return {
                'guardian_type': data['guardian_type'],
                'relationship_to_athlete': data.get('relationship_to_athlete'),
                'permissions': data.get('permissions')
            }
        
        return {}
    
    @staticmethod
    def get_role_requirements() -> Dict:
        """Get all role requirements for documentation/schema generation"""
        return {
            'athlete': {
                'required': ['sport_id'],
                'optional': ['position', 'team', 'custom_baselines'],
                'description': 'Sports athlete account'
            },
            'coach': {
                'required': [],
                'optional': ['specialization', 'years_of_experience'],
                'description': 'Coach/trainer account'
            },
            'physiotherapist': {
                'required': ['license_number'],
                'optional': ['specialization'],
                'description': 'Licensed physiotherapist account'
            },
            'parent': {
                'required': ['guardian_type'],
                'optional': ['relationship_to_athlete', 'permissions'],
                'description': 'Parent/guardian account'
            }
        }
