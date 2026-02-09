import json
import requests
from datetime import datetime

DATA_FILE_PATH = "data/teacher_materials.json"


def get_materials():
    """
    Fetch teacher materials from GitHub JSON file.
    Returns a list of material dictionaries.
    """
    try:
        from github_utils import _get_github_config as get_config
        config = get_config()
        url = f"https://raw.githubusercontent.com/{config['repo']}/{config['branch']}/{DATA_FILE_PATH}"

        response = requests.get(url)
        if response.status_code == 404:
            # File doesn't exist yet, return empty list
            return []

        response.raise_for_status()
        materials = response.json()
        return materials if isinstance(materials, list) else []
    except Exception as e:
        # Return empty list instead of raising error for better resilience
        return []


def save_materials(materials):
    """
    Save teacher materials to GitHub JSON file.
    """
    try:
        from github_utils import upload_to_github

        # Convert materials to JSON
        json_bytes = json.dumps(materials, indent=2).encode('utf-8')

        # Upload to GitHub
        upload_to_github(
            file_bytes=json_bytes,
            file_path=DATA_FILE_PATH,
            commit_message="Update teacher materials"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to save materials: {e}")


def add_material(course_code, course_title, filename, file_url, 
                 section=None, uploaded_at=None, uploaded_by=None, material_type=None):
    """
    Add a new material.
    
    Args:
        course_code: The course code (e.g., UE22CS202)
        course_title: The course title
        filename: The filename
        file_url: The URL to the file
        section: Not used anymore (for backward compatibility)
        uploaded_at: Timestamp of upload (if not provided, uses current time)
        uploaded_by: User who uploaded (if not provided, uses 'Unknown')
        material_type: Type of material (Slides, Notes, Assignments, etc.)
    """
    materials = get_materials()

    # Generate a simple ID
    material_id = f"mat_{len(materials) + 1}_{int(datetime.utcnow().timestamp())}"

    new_material = {
        "id": material_id,
        "course_code": course_code,
        "course_title": course_title,
        "filename": filename,
        "file_url": file_url,
        "material_type": material_type or "Other",
        "uploaded_by": uploaded_by or "Unknown",
        "uploaded_at": uploaded_at or datetime.utcnow().isoformat()
    }

    materials.append(new_material)
    save_materials(materials)
    return material_id


def delete_material(course_code, filename):
    """
    Delete a material by course code and filename.
    """
    materials = get_materials()
    
    # Remove from materials list
    materials = [m for m in materials 
                 if not (m.get("course_code") == course_code and m.get("filename") == filename)]
    save_materials(materials)


def get_materials_by_section(class_id=None, section=None):
    """
    Get all materials.
    Parameters are kept for backward compatibility but ignored.
    """
    materials = get_materials()
    return materials

