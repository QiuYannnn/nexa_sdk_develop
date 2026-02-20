"""
Template Manager Module

Provides default profile templates and template management.

Features:
- 5 default profile templates (Work, Personal, Photography, Development, Academic)
- Template preview functionality
- Create profiles from templates
- Custom template creation from existing profiles
- Template customization options
"""
from __future__ import annotations

from typing import Any

from file_organizer.services.intelligence.profile_manager import Profile, ProfileManager


class TemplateManager:
    """
    Template management system with default templates.

    Features:
    - Predefined templates for common workflows
    - Template preview before application
    - Create profiles from templates
    - Create custom templates from profiles
    - Template customization
    """

    # Default templates
    TEMPLATES = {
        "work": {
            "name": "Work Profile",
            "description": "Corporate document organization with formal conventions",
            "preferences": {
                "global": {
                    "naming_patterns": {
                        "date_format": "YYYY-MM-DD",
                        "separator": "_",
                        "case_style": "title",
                        "include_metadata": True
                    },
                    "folder_mappings": {
                        "documents": "Documents/Work",
                        "spreadsheets": "Documents/Work/Spreadsheets",
                        "presentations": "Documents/Work/Presentations",
                        "reports": "Documents/Work/Reports",
                        "contracts": "Documents/Work/Legal/Contracts"
                    },
                    "category_overrides": {
                        "invoice": "financial",
                        "contract": "legal",
                        "presentation": "work",
                        "report": "work"
                    }
                },
                "directory_specific": {}
            },
            "learned_patterns": {
                "folder_structure": "date_based",
                "organization_style": "client_project",
                "naming_style": "formal"
            },
            "confidence_data": {
                "naming_patterns": 0.9,
                "folder_mappings": 0.85,
                "category_overrides": 0.9
            }
        },
        "personal": {
            "name": "Personal Profile",
            "description": "Casual organization for personal files with minimal structure",
            "preferences": {
                "global": {
                    "naming_patterns": {
                        "date_format": "MM-DD-YYYY",
                        "separator": "-",
                        "case_style": "lower",
                        "include_metadata": False
                    },
                    "folder_mappings": {
                        "photos": "Pictures",
                        "videos": "Videos",
                        "documents": "Documents/Personal",
                        "music": "Music",
                        "downloads": "Downloads"
                    },
                    "category_overrides": {
                        "vacation": "personal",
                        "family": "personal",
                        "hobby": "personal"
                    }
                },
                "directory_specific": {}
            },
            "learned_patterns": {
                "folder_structure": "topic_based",
                "organization_style": "minimal",
                "naming_style": "casual"
            },
            "confidence_data": {
                "naming_patterns": 0.7,
                "folder_mappings": 0.75,
                "category_overrides": 0.7
            }
        },
        "photography": {
            "name": "Photography Profile",
            "description": "Date and event-based organization for photographers",
            "preferences": {
                "global": {
                    "naming_patterns": {
                        "date_format": "YYYY-MM-DD",
                        "separator": "_",
                        "include_event": True,
                        "include_camera": True,
                        "case_style": "lower"
                    },
                    "folder_mappings": {
                        "raw": "Photos/RAW",
                        "edited": "Photos/Edited",
                        "exports": "Photos/Exports",
                        "originals": "Photos/Originals",
                        "projects": "Photos/Projects"
                    },
                    "category_overrides": {
                        ".raw": "raw",
                        ".cr2": "raw",
                        ".nef": "raw",
                        ".arw": "raw",
                        ".dng": "raw",
                        ".jpg": "edited",
                        ".jpeg": "edited",
                        ".png": "export"
                    }
                },
                "directory_specific": {}
            },
            "learned_patterns": {
                "folder_structure": "year_month",
                "organization_style": "event_based",
                "naming_style": "metadata_rich",
                "raw_vs_processed": "separate"
            },
            "confidence_data": {
                "naming_patterns": 0.95,
                "folder_mappings": 0.9,
                "category_overrides": 0.95
            }
        },
        "development": {
            "name": "Development Profile",
            "description": "Project-based organization for software developers",
            "preferences": {
                "global": {
                    "naming_patterns": {
                        "case_style": "snake_case",
                        "separator": "_",
                        "include_version": True,
                        "date_format": "YYYY-MM-DD"
                    },
                    "folder_mappings": {
                        "projects": "Projects",
                        "repositories": "Repos",
                        "documentation": "Docs",
                        "scripts": "Scripts",
                        "configs": "Config"
                    },
                    "category_overrides": {
                        ".py": "python",
                        ".js": "javascript",
                        ".ts": "typescript",
                        ".java": "java",
                        ".cpp": "cpp",
                        ".go": "golang",
                        ".rs": "rust",
                        ".md": "documentation"
                    }
                },
                "directory_specific": {}
            },
            "learned_patterns": {
                "folder_structure": "project_based",
                "organization_style": "language_specific",
                "naming_style": "technical",
                "version_control": "aware",
                "ignore_patterns": ["node_modules", ".git", "__pycache__", "build", "dist"]
            },
            "confidence_data": {
                "naming_patterns": 0.85,
                "folder_mappings": 0.9,
                "category_overrides": 0.95
            }
        },
        "academic": {
            "name": "Academic Profile",
            "description": "Course and research organization for students and researchers",
            "preferences": {
                "global": {
                    "naming_patterns": {
                        "date_format": "YYYY-MM-DD",
                        "separator": "_",
                        "include_course": True,
                        "include_version": True,
                        "case_style": "title"
                    },
                    "folder_mappings": {
                        "courses": "Academic/Courses",
                        "research": "Academic/Research",
                        "papers": "Academic/Papers",
                        "notes": "Academic/Notes",
                        "presentations": "Academic/Presentations",
                        "references": "Academic/References"
                    },
                    "category_overrides": {
                        "syllabus": "course_material",
                        "assignment": "coursework",
                        "exam": "coursework",
                        "paper": "research",
                        "thesis": "research",
                        "citation": "reference"
                    }
                },
                "directory_specific": {}
            },
            "learned_patterns": {
                "folder_structure": "course_semester",
                "organization_style": "hierarchical",
                "naming_style": "academic",
                "version_control": "draft_versioning",
                "citation_style": "apa"
            },
            "confidence_data": {
                "naming_patterns": 0.85,
                "folder_mappings": 0.9,
                "category_overrides": 0.85
            }
        }
    }

    def __init__(self, profile_manager: ProfileManager):
        """
        Initialize template manager.

        Args:
            profile_manager: ProfileManager instance
        """
        self.profile_manager = profile_manager
        import copy
        self._templates = copy.deepcopy(self.TEMPLATES)

    def list_templates(self) -> list[str]:
        """
        List all available template names.

        Returns:
            List of template names
        """
        return list(self._templates.keys())

    def get_template(self, template_name: str) -> dict[str, Any] | None:
        """
        Get template data by name.

        Args:
            template_name: Name of template to retrieve

        Returns:
            Template data dictionary or None if not found
        """
        template_name_lower = template_name.lower()
        if template_name_lower in self._templates:
            return self._templates[template_name_lower].copy()
        return None

    def preview_template(self, template_name: str) -> dict[str, Any] | None:
        """
        Preview template details before applying.

        Args:
            template_name: Name of template to preview

        Returns:
            Dictionary with template preview or None if not found
        """
        template = self.get_template(template_name)
        if template is None:
            print(f"Error: Template '{template_name}' not found")
            print(f"Available templates: {', '.join(self.list_templates())}")
            return None

        # Build preview
        preview = {
            'template_name': template_name.lower(),
            'name': template['name'],
            'description': template['description'],
            'preferences_summary': {
                'naming_patterns': list(template['preferences']['global']['naming_patterns'].keys()),
                'folder_mappings': list(template['preferences']['global']['folder_mappings'].keys()),
                'category_overrides': len(template['preferences']['global']['category_overrides'])
            },
            'learned_patterns': list(template['learned_patterns'].keys()),
            'confidence_levels': template['confidence_data']
        }

        return preview

    def create_profile_from_template(
        self,
        template_name: str,
        profile_name: str,
        customize: dict[str, Any] | None = None
    ) -> Profile | None:
        """
        Create a new profile from a template.

        Args:
            template_name: Name of template to use
            profile_name: Name for the new profile
            customize: Optional customizations to apply to template

        Returns:
            Created Profile object or None on failure
        """
        try:
            # Get template
            template = self.get_template(template_name)
            if template is None:
                print(f"Error: Template '{template_name}' not found")
                return None

            # Check if profile already exists
            if self.profile_manager.profile_exists(profile_name):
                print(f"Error: Profile '{profile_name}' already exists")
                return None

            # Apply customizations if provided
            if customize:
                template = self._apply_customizations(template, customize)

            # Create profile
            profile = self.profile_manager.create_profile(
                profile_name,
                template['description']
            )

            if profile is None:
                return None

            # Update with template data
            success = self.profile_manager.update_profile(
                profile_name,
                preferences=template['preferences'],
                learned_patterns=template['learned_patterns'],
                confidence_data=template['confidence_data']
            )

            if not success:
                # Clean up failed profile creation
                self.profile_manager.delete_profile(profile_name, force=True)
                return None

            return self.profile_manager.get_profile(profile_name)

        except Exception as e:
            print(f"Error creating profile from template: {e}")
            return None

    def _apply_customizations(
        self,
        template: dict[str, Any],
        customize: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Apply customizations to a template.

        Args:
            template: Template data to customize
            customize: Customization options

        Returns:
            Customized template data
        """
        # Deep copy to avoid modifying original
        import copy
        customized = copy.deepcopy(template)

        # Apply naming pattern customizations
        if 'naming_patterns' in customize:
            customized['preferences']['global']['naming_patterns'].update(
                customize['naming_patterns']
            )

        # Apply folder mapping customizations
        if 'folder_mappings' in customize:
            customized['preferences']['global']['folder_mappings'].update(
                customize['folder_mappings']
            )

        # Apply category override customizations
        if 'category_overrides' in customize:
            customized['preferences']['global']['category_overrides'].update(
                customize['category_overrides']
            )

        # Update description if provided
        if 'description' in customize:
            customized['description'] = customize['description']

        return customized

    def create_custom_template(
        self,
        from_profile: str,
        template_name: str
    ) -> bool:
        """
        Create a custom template from an existing profile.

        Args:
            from_profile: Name of profile to create template from
            template_name: Name for the new template

        Returns:
            True if template created successfully, False otherwise
        """
        try:
            # Load profile
            profile = self.profile_manager.get_profile(from_profile)
            if profile is None:
                print(f"Error: Profile '{from_profile}' not found")
                return False

            # Check if template name already exists
            if template_name.lower() in self._templates:
                print(f"Error: Template '{template_name}' already exists")
                return False

            # Create template data from profile
            template_data = {
                'name': profile.profile_name,
                'description': profile.description,
                'preferences': profile.preferences,
                'learned_patterns': profile.learned_patterns,
                'confidence_data': profile.confidence_data
            }

            # Add to templates (in-memory only, not persisted)
            # For persistence, would need to save to file
            self._templates[template_name.lower()] = template_data

            print(f"Created custom template '{template_name}' from profile '{from_profile}'")
            print("Note: Custom templates are not persisted and will be lost on restart")

            return True

        except Exception as e:
            print(f"Error creating custom template: {e}")
            return False

    def get_template_recommendations(
        self,
        file_types: list[str] | None = None,
        use_case: str | None = None
    ) -> list[str]:
        """
        Get template recommendations based on file types or use case.

        Args:
            file_types: List of file extensions (e.g., ['.py', '.js'])
            use_case: Description of use case

        Returns:
            List of recommended template names
        """
        recommendations = []

        if file_types:
            # Recommend based on file types
            file_types_lower = [ft.lower() for ft in file_types]

            # Check for development files
            dev_extensions = ['.py', '.js', '.ts', '.java', '.cpp', '.go', '.rs', '.c', '.h']
            if any(ext in file_types_lower for ext in dev_extensions):
                recommendations.append('development')

            # Check for image files
            image_extensions = ['.jpg', '.jpeg', '.png', '.raw', '.cr2', '.nef', '.arw']
            if any(ext in file_types_lower for ext in image_extensions):
                recommendations.append('photography')

            # Check for document files
            doc_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']
            if any(ext in file_types_lower for ext in doc_extensions):
                recommendations.append('work')
                recommendations.append('academic')

        if use_case:
            use_case_lower = use_case.lower()

            # Keyword-based recommendations
            if any(word in use_case_lower for word in ['work', 'business', 'corporate', 'office']):
                recommendations.append('work')

            if any(word in use_case_lower for word in ['personal', 'home', 'family']):
                recommendations.append('personal')

            if any(word in use_case_lower for word in ['photo', 'picture', 'camera', 'shoot']):
                recommendations.append('photography')

            if any(word in use_case_lower for word in ['code', 'program', 'develop', 'software']):
                recommendations.append('development')

            if any(word in use_case_lower for word in ['school', 'university', 'research', 'study']):
                recommendations.append('academic')

        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for template in recommendations:
            if template not in seen:
                seen.add(template)
                unique_recommendations.append(template)

        return unique_recommendations

    def compare_templates(
        self,
        template_names: list[str]
    ) -> dict[str, Any] | None:
        """
        Compare multiple templates side by side.

        Args:
            template_names: List of template names to compare

        Returns:
            Comparison dictionary or None on error
        """
        try:
            comparison = {
                'templates': [],
                'differences': []
            }

            templates = []
            for name in template_names:
                template = self.get_template(name)
                if template is None:
                    print(f"Warning: Template '{name}' not found, skipping")
                    continue
                templates.append({'name': name, 'data': template})

            if len(templates) < 2:
                print("Need at least 2 valid templates to compare")
                return None

            # Add template summaries
            for t in templates:
                comparison['templates'].append({
                    'name': t['name'],
                    'description': t['data']['description'],
                    'naming_style': t['data']['learned_patterns'].get('naming_style'),
                    'folder_structure': t['data']['learned_patterns'].get('folder_structure'),
                    'num_folder_mappings': len(t['data']['preferences']['global']['folder_mappings']),
                    'num_category_overrides': len(t['data']['preferences']['global']['category_overrides'])
                })

            return comparison

        except Exception as e:
            print(f"Error comparing templates: {e}")
            return None
