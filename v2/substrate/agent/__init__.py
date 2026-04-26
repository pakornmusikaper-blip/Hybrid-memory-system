"""
Substrate Agent — Background Intelligence for Hybrid Memory System v2

A conscious-subconscious architecture for AI memory:
- Conscious: This agent (main session)
- Substrate: Background agent with own memory that runs continuously
"""

from .core import SubstrateAgent
from .growth import GrowthSystem

__version__ = "2.1.0"
__all__ = ["SubstrateAgent", "GrowthSystem"]
