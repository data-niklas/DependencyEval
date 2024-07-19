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
    predict_correct_completion_symbol: bool = True
    force_custom_pad: bool = False
    masked_gen: bool = True
    enabled: bool = (
        True  # quick setting to disable all processors, overrides other settings
    )


@dataclass
class Dataset:
    name: str
    items: List[Dict[str, Any]]
