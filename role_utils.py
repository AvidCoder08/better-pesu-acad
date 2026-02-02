import re
from role_config import SUPERADMIN_IDS, CR_IDS_BY_CLASS


def _get_personal(profile):
    if isinstance(profile, dict):
        return profile.get("personal", {})
    return getattr(profile, "personal", {})


def _get_value(personal, key, default=""):
    if isinstance(personal, dict):
        return personal.get(key, default)
    return getattr(personal, key, default)


def get_user_ids(profile):
    personal = _get_personal(profile)
    srn = str(_get_value(personal, "srn", "")).strip()
    email = str(_get_value(personal, "email_id", "")).strip()
    pesu_id = str(_get_value(personal, "pesu_id", "")).strip()
    ids = {srn.lower(), email.lower(), pesu_id.lower()}
    return {i for i in ids if i}


def get_class_id(profile):
    personal = _get_personal(profile)
    program = str(_get_value(personal, "program", "")).strip()
    branch = str(_get_value(personal, "branch", "")).strip()
    section = str(_get_value(personal, "section", "")).strip()
    semester_raw = str(_get_value(personal, "semester", "")).strip()

    match = re.search(r"\d+", semester_raw)
    semester = match.group(0) if match else semester_raw

    def clean(value):
        return value.replace(" ", "")

    return f"{clean(program)}-{clean(branch)}-Sem{clean(semester)}-{clean(section)}"


def is_superadmin(profile):
    user_ids = get_user_ids(profile)
    return any(uid in {x.lower() for x in SUPERADMIN_IDS} for uid in user_ids)


def is_cr(profile):
    class_id = get_class_id(profile)
    user_ids = get_user_ids(profile)
    allowed_ids = {x.lower() for x in CR_IDS_BY_CLASS.get(class_id, set())}
    return any(uid in allowed_ids for uid in user_ids)
