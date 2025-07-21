from typing import Tuple

from model.domain import Semester, Subject
from model.repositories.data_persistence import DataPersistence


def add_subject(sem_obj: Semester, code: str, name: str, sync_subject: bool) -> Tuple[bool, str]:
    """
    Adds a new subject to the given semester object.

    Args:
        sem_obj (Semester): The semester object to which the subject will be added.
        code (str): The unique code of the subject.
        name (str): The name of the subject.
        sync_subject (bool): Flag indicating whether to synchronize the subject with an external system.

    Returns:
        tuple: A tuple containing a boolean and a message.
            - bool: True if the subject was added successfully, False otherwise.
            - str: A message indicating the result of the operation.

    Raises:
        None
    """
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


def set_total_mark(subject: Subject, total_mark: float, data_persistence: DataPersistence) -> Tuple[bool, str]:
    """
    Sets the total mark for a given subject and persists the data.

    Args:
        subject (Subject): The subject object for which the total mark is to be set.
        total_mark (float): The total mark to be assigned to the subject.
        data_persistence (DataPersistence): An object responsible for saving data persistence.

    Returns:
        tuple: A tuple containing a boolean and a message.
            - bool: True if the total mark was set successfully, False otherwise.
            - str: A message indicating the result of the operation.
    """
    if subject is None:
        return False, "Subject not found."
    subject.total_mark = total_mark
    data_persistence.save_data(data_persistence.data)
    return True, f"Total Mark for '{subject.subject_code}' set to {total_mark}."
