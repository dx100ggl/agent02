from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class ToolSchema:
    """
    Schema describing a tool's expected arguments and output.
    """
    name: str
    description: str
    args: Dict[str, Any]          # {arg_name: type or description}
    returns: Optional[str] = None # description of return type

    def validate_args(self, provided: Dict[str, Any]) -> bool:
        """
        Basic argument validation: ensure required args exist.
        """
        for key in self.args.keys():
            if key not in provided:
                return False
        return True
