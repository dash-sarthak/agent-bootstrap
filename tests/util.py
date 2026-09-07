"""Shared test helpers: filesystem tree hashing for determinism checks."""
import hashlib
from pathlib import Path


def tree_state(root):
    """Return {relative_path: sha256_hex} for every regular file under root."""
    root = Path(root)
    if not root.exists():
        return {}
    state = {}
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        state[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return state


def tree_manifest(root):
    """Return manifest lines '<sha256>  <relpath>', sorted by path."""
    return [f"{digest}  {rel}" for rel, digest in sorted(tree_state(root).items())]
