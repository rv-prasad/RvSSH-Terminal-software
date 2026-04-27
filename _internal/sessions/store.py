import json
from pathlib import Path

from utils.paths import app_base_dir

FILE = app_base_dir() / "sessions" / "sessions.json"
FILE.parent.mkdir(parents=True, exist_ok=True)

#FILE = Path(__file__).with_name("sessions.json")


# -----------------------------
# Legacy (flat list) functions
# -----------------------------
def load_sessions():
    """
    Legacy loader:
    Returns a flat list of session dicts.
    If sessions.json uses tree format, it will be flattened.
    """
    data = load_sessions_tree()
    return flatten_sessions(data)


def save_sessions(sessions):
    """
    Legacy saver:
    Saves a flat list as tree format under a default folder.
    """
    tree = {
        "folders": [
            {"type": "folder", "name": "Default", "children": []}
        ]
    }
    for s in sessions or []:
        tree["folders"][0]["children"].append({
            "type": "session",
            "name": s.get("name", ""),
            "host": s.get("host", s.get("name", "")),
            "port": s.get("port", 22),
        })
    save_sessions_tree(tree)


# -----------------------------
# Tree (folder/session) functions
# -----------------------------
def load_sessions_tree():
    """
    Loads sessions in tree format:
      { "folders": [ folder_nodes... ] }

    Supports legacy list format:
      [ {name, host, port?}, ... ]
    and upgrades it in memory.
    """
    if not FILE.exists():
        return {"folders": []}

    txt = FILE.read_text(encoding="utf-8").strip()
    if not txt:
        return {"folders": []}

    data = json.loads(txt)

    # Legacy format: list of sessions
    if isinstance(data, list):
        return _wrap_legacy_list_to_tree(data)

    # New tree format
    if isinstance(data, dict) and "folders" in data:
        return data

    # Unknown format fallback
    return {"folders": []}


def save_sessions_tree(tree_data):
    """
    Saves tree format to sessions.json.
    """
    FILE.write_text(json.dumps(tree_data, indent=2), encoding="utf-8")


def _wrap_legacy_list_to_tree(items):
    children = []
    for s in items:
        children.append({
            "type": "session",
            "name": s.get("name", ""),
            "host": s.get("host", s.get("name", "")),
            "port": s.get("port", 22),
        })
    return {
        "folders": [
            {"type": "folder", "name": "Default", "children": children}
        ]
    }


def flatten_sessions(tree_data):
    """
    Flattens tree structure into a list of sessions for legacy callers.
    """
    out = []

    def walk(node):
        if node.get("type") == "session":
            out.append(node)
        elif node.get("type") == "folder":
            for ch in node.get("children", []):
                walk(ch)

    for f in tree_data.get("folders", []):
        walk(f)

    return out