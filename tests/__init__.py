"""Test package for agent_prompt_sections.

Adds the ``src`` layout directory to ``sys.path`` so the tests can import the
package directly with the standard-library ``unittest`` runner, without an
editable install::

    python3 -m unittest discover -s tests
"""

import os
import sys

_SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
