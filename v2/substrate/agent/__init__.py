"""
Substrate Agent — Background Intelligence for Hybrid Memory System v2

A conscious-subconscious architecture for AI memory:
- Conscious: This agent (main session)
- Substrate: Background agent with own memory that runs continuously
"""

from .core import SubstrateAgent
from .growth import GrowthSystem
from .bridge import ConsciousnessBridge, IntuitionGenerator

__version__ = "2.2.0"
__all__ = ["SubstrateAgent", "GrowthSystem", "ConsciousnessBridge", "IntuitionGenerator"]
