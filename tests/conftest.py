import sys
from pathlib import Path

# audiodb.py uses `from ai.retriever import ...` (absolute, not src.ai),
# so src/ must be on sys.path for that import to resolve.
_src = Path(__file__).parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))
