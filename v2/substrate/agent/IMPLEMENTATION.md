# Substrate Agent Python Implementation

Status: Alpha
Date: 2026-04-27

## Core Agent Implementation

This is the core Substrate Agent implementation using Qwen 1.8B.

## Installation Requirements

```text
transformers>=4.35.0
torch>=2.0.0
accelerate>=0.25.0
pyyaml>=6.0
```

## config/model_config.yaml

```yaml
model:
  name: Qwen/Qwen2-1.5B
  # Swap to Qwen/Qwen2-1.8B when ready
  trust_remote_code: true
  
runtime:
  device: cuda  # or cpu if no GPU
  max_memory_gb: 4
  
prompts:
  absorb: |
    You are Substrate, a background intelligence agent.
    Analyze this context and update your understanding.
    
    Context: {context}
    
    Identify:
    1. Key facts and their relationships
    2. Patterns you observe
    3. What might be needed next
    4. Any contradictions or gaps
    
  weave: |
    Weave context from multiple sources.
    
    Sources: {sources}
    
    Create a coherent context bundle that includes:
    - Current state
    - Relevant history
    - Connections to other knowledge
    - Anticipations for next steps
    
  belief: |
    Based on accumulated context, form a belief.
    
    Context: {context}
    Related beliefs: {related}
    
    State the belief clearly and assign a confidence score (0-1).
    Higher confidence requires more consistent evidence.
    
  validate: |
    Validate this belief against known facts.
    
    Belief: {belief}
    Known facts: {facts}
    
    Return: confirm | contradict | modify
    If modify, state the corrected belief.
```

## Implementation: agent/core.py

```python
"""
Substrate Agent — Background Intelligence for Hybrid Memory System v2
"""

import os
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
import threading
import time

class SubstrateAgent:
    """
    The Substrate Agent
    
    A background intelligence that:
    - Runs continuously
    - Absorbs context from memory layers
    - Forms and updates beliefs
    - Prepares anticipatory context
    - Grows over time through experience
    
    Never interrupts conscious layer. Only serves when called.
    """
    
    def __init__(self, memory_root: Path, config_path: Path):
        self.memory_root = Path(memory_root)
        self.config = self.load_config(config_path)
        self.own_memory = OwnMemory(self.memory_root / "substrate" / "own_memory")
        self.anticipation_cache = AnticipationCache(
            self.memory_root / "substrate" / "own_memory" / "anticipation_cache"
        )
        self.growth_tracker = GrowthTracker(
            self.memory_root / "substrate" / "own_memory" / "growth_log"
        )
        
        # Model will be loaded lazily
        self.model = None
        self.model_lock = threading.Lock()
        
        # Background loop
        self._running = False
        self._thread = None
        
    def load_config(self, config_path: Path) -> Dict:
        with open(config_path) as f:
            return yaml.safe_load(f)
            
    def load_model(self):
        """Load Qwen model. Lazy loading to save memory."""
        if self.model is not None:
            return self.model
            
        with self.model_lock:
            if self.model is not None:
                return self.model
                
            from transformers import AutoModelForCausalLM, AutoTokenizer
            model_name = self.config["model"]["name"]
            
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map=self.config["runtime"].get("device", "cpu"),
                torch_dtype=torch.float16,
            )
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            return self.model
            
    # ─────────────────────────────────────────────────────────────
    # CORE OPERATIONS
    # ─────────────────────────────────────────────────────────────
    
    def absorb(self, context: Dict) -> None:
        """
        Absorb new context from the system.
        This is the primary entry point for new information.
        """
        # 1. Weave context
        woven = self.weave(context)
        
        # 2. Form or update beliefs
        beliefs = self.form_beliefs(woven)
        
        # 3. Forge connections
        self.forge_connections(woven)
        
        # 4. Validate
        validated = self.validate(beliefs)
        
        # 5. Update own memory
        self.own_memory.update_beliefs(validated)
        
        # 6. Prepare anticipations
        self.prepare_anticipations(woven)
        
        # 7. Log growth
        self.growth_tracker.record(
            operation="absorb",
            beliefs_count=len(validated),
            context=context.get("source", "unknown")
        )
        
    def weave(self, context: Dict) -> Dict:
        """
        Weave context from multiple memory layers.
        Returns a coherent context bundle.
        """
        # Check anticipation cache first
        cached = self.anticipation_cache.get(context.get("query", ""))
        if cached and cached.get("fresh"):
            return cached
            
        # Gather relevant sources
        relevant_structured = self.gather_structured(context)
        relevant_wiki = self.gather_wiki(context)
        relevant_history = self.own_memory.get_recent_beliefs()
        
        # Create weave prompt
        prompt = self.config["prompts"]["weave"].format(
            sources={
                "structured": relevant_structured,
                "wiki": relevant_wiki,
                "history": relevant_history,
                "new_context": context
            }
        )
        
        # Generate woven context
        model = self.load_model()
        response = self.generate(prompt)
        
        woven = {
            "context": context,
            "structured": relevant_structured,
            "wiki": relevant_wiki,
            "history": relevant_history,
            "woven_content": response,
            "timestamp": datetime.now().isoformat(),
            "fresh": True
        }
        
        return woven
        
    def form_beliefs(self, woven: Dict) -> List[Dict]:
        """
        Form new beliefs from woven context.
        """
        model = self.load_model()
        beliefs = []
        
        prompt = self.config["prompts"]["belief"].format(
            context=woven.get("woven_content", ""),
            related=woven.get("history", [])
        )
        
        response = self.generate(prompt)
        
        # Parse beliefs from response
        # Implementation note: Parse structured belief objects from LLM output
        # Each belief should have: statement, confidence, subject, evidence
        
        return beliefs
        
    def forge_connections(self, woven: Dict) -> None:
        """
        Find and forge connections between existing knowledge.
        """
        existing_beliefs = self.own_memory.get_all_beliefs()
        
        for belief in existing_beliefs:
            for other_belief in existing_beliefs:
                if belief["id"] == other_belief["id"]:
                    continue
                    
                # Check for implicit connections
                if self.implicitly_connected(belief, other_belief):
                    self.own_memory.link_beliefs(belief["id"], other_belief["id"])
                    
    def validate(self, beliefs: List[Dict]) -> List[Dict]:
        """
        Validate beliefs against known facts.
        """
        sources_root = self.memory_root / "sources"
        
        validated = []
        for belief in beliefs:
            validated_belief = belief.copy()
            
            # Check against facts
            for fact in self.gather_facts(sources_root):
                if self.contradicts(belief, fact):
                    validated_belief["confidence"] *= 0.5
                    validated_belief["needs_correction"] = True
                    
            # Age decay
            age_days = (datetime.now() - datetime.fromisoformat(belief["created"])).days
            if age_days > 30:
                validated_belief["confidence"] *= (0.9 ** (age_days - 30))
                
            validated.append(validated_belief)
            
        return validated
        
    def prepare_anticipations(self, woven: Dict) -> None:
        """
        Prepare anticipatory context based on current situation.
        """
        scenario = woven.get("context", {}).get("scenario", "")
        
        if not scenario:
            return
            
        # Check if we have relevant patterns
        patterns = self.own_memory.get_relevant_patterns(woven)
        
        # Generate anticipation
        anticipation = {
            "scenario": scenario,
            "context_bundle": {
                "structured": woven.get("structured", []),
                "beliefs": self.own_memory.get_relevant_beliefs(woven),
                "patterns": patterns
            },
            "created": datetime.now().isoformat(),
            "freshness_hours": self.config.get("anticipation", {}).get("freshness_hours", 24)
        }
        
        self.anticipation_cache.store(scenario, anticipation)
        
    # ─────────────────────────────────────────────────────────────
    # SERVICE OPERATIONS
    # ─────────────────────────────────────────────────────────────
    
    def serve(self, query: str) -> Dict:
        """
        Serve context to conscious layer when requested.
        This is the primary interface for the conscious agent.
        """
        # Check anticipation cache
        cached = self.anticipation_cache.get(query)
        if cached and cached.get("fresh"):
            return {
                "source": "anticipation_cache",
                "data": cached,
                "confidence": 0.9
            }
            
        # Weave fresh
        woven = self.weave({"query": query})
        
        return {
            "source": "woven",
            "data": woven,
            "confidence": 0.7
        }
        
    def start(self):
        """Start the background processing loop."""
        if self._running:
            return
            
        self._running = True
        self._thread = threading.Thread(target=self._background_loop, daemon=True)
        self._thread.start()
        
        self.growth_tracker.record(operation="start")
        
    def stop(self):
        """Stop the background processing loop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
            
        self.growth_tracker.record(operation="stop")
        
    def _background_loop(self):
        """Continuous background processing."""
        cycle_seconds = self.config.get("operation", {}).get("cycle_seconds", 60)
        
        while self._running:
            try:
                # Check for new context
                new_context = self.poll_context_sources()
                
                if new_context:
                    self.absorb(new_context)
                    
                # Validate stale beliefs
                self.validate_stale_beliefs()
                
                # Forge pending connections
                self.forge_pending_connections()
                
                # Update anticipations
                self.refresh_anticipations()
                
            except Exception as e:
                self.growth_tracker.record(
                    operation="error",
                    error=str(e)
                )
                
            time.sleep(cycle_seconds)
            
    # ─────────────────────────────────────────────────────────────
    # HELPER METHODS
    # ─────────────────────────────────────────────────────────────
    
    def generate(self, prompt: str) -> str:
        """Generate text using the model."""
        model = self.load_model()
        inputs = self.tokenizer(prompt, return_tensors="pt").to(model.device)
        
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.7,
            do_sample=True
        )
        
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
    def gather_structured(self, context: Dict) -> List[Dict]:
        """Gather relevant structured records."""
        # Implementation: search structured/ for relevant records
        return []
        
    def gather_wiki(self, context: Dict) -> List[Dict]:
        """Gather relevant wiki pages."""
        # Implementation: search wiki/ for relevant pages
        return []
        
    def gather_facts(self, sources_root: Path) -> List[Dict]:
        """Gather facts from sources/ for validation."""
        # Implementation: read sources/ and extract facts
        return []
        
    def implicitly_connected(self, belief1: Dict, belief2: Dict) -> bool:
        """Check if two beliefs are implicitly connected."""
        # Implementation: compare subjects, objects, timelines
        return False
        
    def contradicts(self, belief: Dict, fact: Dict) -> bool:
        """Check if a belief contradicts a fact."""
        # Implementation: compare statements
        return False
        
    def poll_context_sources(self) -> Optional[Dict]:
        """Poll for new context from various sources."""
        # Implementation: check session corpus, recent changes, etc.
        return None
        
    def validate_stale_beliefs(self):
        """Validate beliefs older than threshold."""
        stale = self.own_memory.get_stale_beliefs(days=30)
        for belief in stale:
            validated = self.validate([belief])
            self.own_memory.update_beliefs(validated)
            
    def forge_pending_connections(self):
        """Forge connections that were deferred."""
        pending = self.own_memory.get_pending_connections()
        for belief_id, target_id in pending:
            self.own_memory.link_beliefs(belief_id, target_id)
            
    def refresh_anticipations(self):
        """Refresh stale anticipations."""
        stale = self.anticipation_cache.get_stale()
        for scenario in stale:
            woven = self.weave({"scenario": scenario})
            self.prepare_anticipations(woven)
```

## Implementation: OwnMemory

```python
"""
OwnMemory — The substrate's private memory layer
"""

from pathlib import Path
import json
from datetime import datetime
from typing import List, Dict, Optional

class OwnMemory:
    """
    The Substrate Agent's own memory.
    Separate from the public memory layers.
    Only the Substrate Agent reads and writes here.
    """
    
    def __init__(self, root: Path):
        self.root = Path(root)
        self.beliefs_dir = self.root / "beliefs"
        self.patterns_dir = self.root / "patterns"
        self.growth_dir = self.root / "growth_log"
        
        # Ensure directories exist
        for d in [self.beliefs_dir, self.patterns_dir, self.growth_dir]:
            d.mkdir(parents=True, exist_ok=True)
            
    # ─────────────────────────────────────────────────────────────
    # BELIEFS
    # ─────────────────────────────────────────────────────────────
    
    def update_beliefs(self, beliefs: List[Dict]) -> None:
        """Update beliefs in own memory."""
        for belief in beliefs:
            belief_id = belief.get("id")
            if not belief_id:
                continue
                
            path = self.beliefs_dir / f"{belief_id}.yaml"
            
            # Update modified time
            belief["updated"] = datetime.now().isoformat()
            
            with open(path, "w") as f:
                yaml.dump(belief, f)
                
    def get_all_beliefs(self) -> List[Dict]:
        """Get all beliefs from own memory."""
        beliefs = []
        for path in self.beliefs_dir.glob("*.yaml"):
            with open(path) as f:
                beliefs.append(yaml.safe_load(f))
        return beliefs
        
    def get_recent_beliefs(self, limit: int = 10) -> List[Dict]:
        """Get most recent beliefs."""
        beliefs = self.get_all_beliefs()
        beliefs.sort(key=lambda b: b.get("updated", ""), reverse=True)
        return beliefs[:limit]
        
    def get_stale_beliefs(self, days: int = 30) -> List[Dict]:
        """Get beliefs that haven't been updated in N days."""
        beliefs = self.get_all_beliefs()
        stale = []
        
        for belief in beliefs:
            updated = datetime.fromisoformat(belief.get("updated", ""))
            if (datetime.now() - updated).days > days:
                stale.append(belief)
                
        return stale
        
    def get_relevant_beliefs(self, context: Dict) -> List[Dict]:
        """Get beliefs relevant to current context."""
        all_beliefs = self.get_all_beliefs()
        
        relevant = []
        for belief in all_beliefs:
            # Simple relevance: subject match or related
            if self.is_relevant(belief, context):
                relevant.append(belief)
                
        return relevant
        
    def is_relevant(self, belief: Dict, context: Dict) -> bool:
        """Check if belief is relevant to context."""
        # Implementation: match subject, tags, related IDs
        return True
        
    def link_beliefs(self, belief_id: str, target_id: str) -> None:
        """Link two beliefs as related."""
        belief_path = self.beliefs_dir / f"{belief_id}.yaml"
        
        if belief_path.exists():
            with open(belief_path) as f:
                belief = yaml.safe_load(f)
                
            if "related_beliefs" not in belief:
                belief["related_beliefs"] = []
                
            if target_id not in belief["related_beliefs"]:
                belief["related_beliefs"].append(target_id)
                
            with open(belief_path, "w") as f:
                yaml.dump(belief, f)
                
    def get_pending_connections(self) -> List[tuple]:
        """Get connections waiting to be forged."""
        # Implementation: track in a pending_connections.json
        return []
        
    # ─────────────────────────────────────────────────────────────
    # PATTERNS
    # ─────────────────────────────────────────────────────────────
    
    def get_relevant_patterns(self, context: Dict) -> List[Dict]:
        """Get patterns relevant to context."""
        patterns = []
        for path in self.patterns_dir.glob("*.yaml"):
            with open(path) as f:
                pattern = yaml.safe_load(f)
                if self.is_relevant(pattern, context):
                    patterns.append(pattern)
        return patterns
```

## Implementation: AnticipationCache

```python
"""
Anticipation Cache — Pre-prepared context for fast serving
"""

from pathlib import Path
import json
from datetime import datetime, timedelta
from typing import Optional, Dict

class AnticipationCache:
    """
    Cache of pre-prepared anticipatory context.
    Makes serving to conscious layer fast and relevant.
    """
    
    def __init__(self, root: Path):
        self.root = Path(root)
        self.ready_dir = self.root / "ready"
        self.ready_dir.mkdir(parents=True, exist_ok=True)
        
    def store(self, scenario: str, anticipation: Dict) -> None:
        """Store an anticipation."""
        safe_name = scenario.replace(" ", "_").replace("/", "-")
        path = self.ready_dir / f"{safe_name}.json"
        
        anticipation["stored_at"] = datetime.now().isoformat()
        
        with open(path, "w") as f:
            json.dump(anticipation, f)
            
    def get(self, scenario: str) -> Optional[Dict]:
        """Get an anticipation if it exists and is fresh."""
        safe_name = scenario.replace(" ", "_").replace("/", "-")
        path = self.ready_dir / f"{safe_name}.json"
        
        if not path.exists():
            return None
            
        with open(path) as f:
            anticipation = json.load(f)
            
        # Check freshness
        stored_at = datetime.fromisoformat(anticipation["stored_at"])
        hours = self.get_freshness_hours()
        
        if datetime.now() - stored_at < timedelta(hours=hours):
            anticipation["fresh"] = True
            return anticipation
        else:
            return None
            
    def get_stale(self) -> list:
        """Get all stale anticipations."""
        stale = []
        
        for path in self.ready_dir.glob("*.json"):
            with open(path) as f:
                anticipation = json.load(f)
                
            stored_at = datetime.fromisoformat(anticipation["stored_at"])
            hours = self.get_freshness_hours()
            
            if datetime.now() - stored_at >= timedelta(hours=hours):
                stale.append(path.stem)
                
        return stale
        
    def get_freshness_hours(self) -> int:
        """Get configured freshness hours."""
        # From config
        return 24
```

## Usage Example

```python
from pathlib import Path
from substrate_agent import SubstrateAgent

# Initialize
memory_root = Path("/home/pakorn/.openclaw/workspace/knowledge-system")
config_path = Path("config/model_config.yaml")

agent = SubstrateAgent(memory_root, config_path)

# Start background processing
agent.start()

# Later, serve context to conscious layer
response = agent.serve("What is the current state of Project X?")

# When done, stop
agent.stop()
```

---

## Next Steps

1. Install dependencies
2. Download Qwen model
3. Configure paths
4. Run first test
5. Observe growth over time