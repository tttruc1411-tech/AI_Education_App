# src/modules/library/manager.py
from .definitions import LIBRARY_FUNCTIONS


def prepare_code_injection(function_id, current_editor_code):
    """
    Searches all categories for function_id and returns injection data.
    Returns a dict with:
        add_import   — bool, whether to prepend the import line
        import_line  — str, the import statement to prepend
        snippet      — str, the usage line to append at cursor
    """
    target_func = None

    for category_data in LIBRARY_FUNCTIONS.values():
        if function_id in category_data["functions"]:
            target_func = category_data["functions"][function_id]
            break

    if not target_func:
        return None

    import_stmt = target_func["import_statement"]
    usage = target_func["usage"]

    # Check if the import already exists in the editor
    if import_stmt not in current_editor_code:
        return {
            "add_import": True,
            "import_line": import_stmt,
            "snippet": usage,
        }

    return {
        "add_import": False,
        "snippet": usage,
    }


def get_function_info(function_id):
    """
    Return the full info dict for a function_id, or None if not found.
    Used by the info panel to display description, params, returns, source.
    """
    for category_data in LIBRARY_FUNCTIONS.values():
        if function_id in category_data["functions"]:
            return category_data["functions"][function_id]
    return None