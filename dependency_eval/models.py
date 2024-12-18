from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ModelConfiguration:
    model: str
    config: Dict[str, Any]
    name: str


@dataclass
class ModelConfigurationGeneration:
    model: str
    config: Dict[str, Any]
    name: str
    items: List[Dict[str, Any]]


@dataclass
class LspGenerationConfig:
    comments_processor: bool = True
    boundary_processor: bool = True
    lsp_processor: bool = True
    chat_history_log_file: Optional[str] = None
    predict_correct_completion_symbol: bool = False
    force_custom_pad: bool = False
    masked_gen: bool = False
    use_completion_context: bool = False
    use_deprecation_context: bool = True
    use_signature_context: bool = True
    enabled: bool = (
        True  # quick setting to disable all processors, overrides other settings
    )


@dataclass
class Dataset:
    name: str
    items: List[Dict[str, Any]]

KINDS = ["modification", "uncommon"]
CODE_KINDS = ["field", "parameter", "function", "method", "block"]
MODIFICATION_KIND = ["addition", "removal", "deprecation", "rename"]