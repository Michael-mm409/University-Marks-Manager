def add_subject(sem_obj, code, name, sync_subject):
    if not code or not name:
        return False, "Subject code and name cannot be empty."
    if code in sem_obj.subjects:
        return False, "Subject code already exists."
    sem_obj.add_subject(code, name, sync_subject=sync_subject)
    return True, f"Added subject {code}."


def delete_subject(sem_obj, code):
    if code not in sem_obj.subjects:
        return False, "Subject not found."
    sem_obj.delete_subject(code)
    return True, f"Deleted subject {code}."


def set_total_mark(subject, total_mark, data_persistence):
    if subject is None:
        return False, "Subject not found."
    subject.total_mark = total_mark
    data_persistence.save_data(data_persistence.data)
    return True, f"Total Mark for '{subject.subject_code}' set to {total_mark}."
