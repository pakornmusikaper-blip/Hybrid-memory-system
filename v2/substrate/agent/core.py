"""
Substrate Agent Core — Background Intelligence

This agent runs in the background and:
1. Absorbs context from memory layers
2. Forms beliefs about the domain
3. Forges connections between knowledge
4. Prepares anticipatory context
5. Grows over time through experience

It has its own memory layer (own_memory/) separate from the public memory.
"""

import os
import json
import yaml
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import threading
import time


class SubstrateAgent:
    """
    The Substrate Agent.
    
    Background intelligence that:
    - Runs continuously
    - Absorbs context
    - Forms beliefs
    - Prepares anticipations
    - Grows autonomously
    
    Never interrupts. Only serves when called.
    """
    
    def __init__(self, memory_root: Path, config_path: Optional[Path] = None):
        self.memory_root = Path(memory_root)
        
        # Load config
        if config_path is None:
            config_path = self.memory_root / "v2" / "substrate" / "config" / "default.yaml"
        self.config = self._load_config(config_path)
        
        # Own memory paths
        self.own_memory_root = self.memory_root / "v2" / "substrate" / "own_memory"
        self.beliefs_dir = self.own_memory_root / "beliefs"
        self.patterns_dir = self.own_memory_root / "patterns"
        self.anticipation_dir = self.own_memory_root / "anticipation_cache"
        self.growth_dir = self.own_memory_root / "growth_log"
        
        # Ensure directories exist
        for d in [self.beliefs_dir, self.patterns_dir, self.anticipation_dir, self.growth_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # Model (lazy loaded)
        self.model = None
        self.tokenizer = None
        self.model_lock = threading.Lock()
        
        # Growth system (v2.1)
        from .growth import GrowthSystem
        self.growth = GrowthSystem(self.memory_root)
        
        # Consciousness Bridge (v2.2)
        from .bridge import ConsciousnessBridge, IntuitionGenerator
        self.bridge = ConsciousnessBridge(self.memory_root)
        self.intuition_gen = IntuitionGenerator(self.bridge)
        
        # Background loop state
        self._running = False
        self._thread = None
        self._last_cycle = None
        
        # Stats
        self.stats = {
            "cycles": 0,
            "beliefs_formed": 0,
            "connections_forged": 0,
            "anticipations_prepared": 0,
            "validations_done": 0,
            "patterns_found": 0,
        }
        
        print(f"[Substrate] Initialized at {self.memory_root}")
        print(f"[Substrate] Model: {self.config['model']['name']}")
        print(f"[Substrate] Device: {self.config['runtime']['device']}")
        print(f"[Substrate] Growth System: v2.1 enabled")
        print(f"[Substrate] Consciousness Bridge: v2.2 enabled")
    
    def _load_config(self, config_path: Path) -> Dict:
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    # ─────────────────────────────────────────────────────────────
    # GPU MANAGEMENT (v2.3)
    # ─────────────────────────────────────────────────────────────
    
    def _setup_gpu(self):
        """Setup GPU configuration."""
        try:
            from .gpu import GPUManager, auto_configure_for_hardware
            
            gpu_manager = GPUManager(self.config)
            gpu_info = gpu_manager.get_gpu_info()
            
            if gpu_info["cuda_available"]:
                print(f"[Substrate] GPU detected: {gpu_info['devices'][0]['name']}")
                print(f"[Substrate] GPU memory: {gpu_info['devices'][0]['total_memory_gb']:.1f}GB")
            else:
                print("[Substrate] No GPU detected, using CPU")
            
            # Auto-configure for hardware
            auto_configure_for_hardware(self.config)
            
            return gpu_manager
        except Exception as e:
            print(f"[Substrate] GPU setup error: {e}, continuing with CPU")
            return None
    
    # ─────────────────────────────────────────────────────────────
    # MODEL MANAGEMENT
    # ─────────────────────────────────────────────────────────────
    
    def load_model(self):
        """Load the Qwen model. Lazy loading to save memory."""
        if self.model is not None:
            return self.model
            
        with self.model_lock:
            if self.model is not None:
                return self.model
                
            model_name = self.config["model"]["name"]
            print(f"[Substrate] Loading model: {model_name}...")
            
            # Setup GPU (v2.3)
            gpu_manager = self._setup_gpu()
            
            from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
            import torch
            
            device = self.config["runtime"]["device"]
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=self.config["model"].get("trust_remote_code", True)
            )
            
            kwargs = {
                "device_map": device,
            }
            
            # Quantization if specified (v2.3 improvements)
            quant = self.config["model"].get("quantization", "none")
            if quant == "4-bit":
                kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype=torch.float16,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            elif quant == "8-bit":
                kwargs["quantization_config"] = BitsAndBytesConfig(
                    load_in_8bit=True
                )
            
            # Set dtype for non-quantized models
            if quant == "none" and device == "cuda":
                kwargs["torch_dtype"] = torch.float16
            elif quant == "none":
                kwargs["torch_dtype"] = torch.float32
            
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                **kwargs
            )
            
            print(f"[Substrate] Model loaded successfully")
            print(f"[Substrate] Device: {device} | Quantization: {quant}")
            return self.model
            
            print(f"[Substrate] Model loaded successfully")
            return self.model
    
    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        """Generate text using the model."""
        try:
            model = self.load_model()
            
            inputs = self.tokenizer(prompt, return_tensors="pt")
            if self.config["runtime"]["device"] != "cpu":
                inputs = {k: v.cuda() for k, v in inputs.items()}
            
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the prompt from response
            if response.startswith(prompt):
                response = response[len(prompt):].strip()
            
            return response
        except Exception as e:
            print(f"[Substrate] Generation error: {e}")
            return f"[Error: {str(e)[:100]}] -- Fallback response"
    
    # ─────────────────────────────────────────────────────────────
    # CORE OPERATIONS
    # ─────────────────────────────────────────────────────────────
    
    def absorb(self, context: Dict) -> None:
        """
        Absorb new context and grow understanding.
        Primary entry point for new information.
        """
        print(f"[Substrate] Absorbing context: {context.get('source', 'unknown')}")
        
        # 1. Weave context from multiple sources
        woven = self.weave(context)
        
        # 2. Form beliefs
        new_beliefs = self.form_beliefs(woven)
        
        # 3. Forge connections
        self.forge_connections(woven)
        
        # 4. Prepare anticipations
        self.prepare_anticipations(woven)
        
        # 5. Log growth
        self._record_growth(
            operation="absorb",
            beliefs_count=len(new_beliefs),
            source=context.get("source", "unknown")
        )
        
        print(f"[Substrate] Absorbed. {len(new_beliefs)} new beliefs formed.")
    
    def weave(self, context: Dict) -> Dict:
        """
        Weave context from memory layers into a coherent bundle.
        """
        # Gather relevant sources
        relevant_structured = self._gather_structured(context)
        relevant_wiki = self._gather_wiki(context)
        recent_beliefs = self._get_recent_beliefs(limit=5)
        
        # Check anticipation cache
        scenario = context.get("scenario", context.get("query", "general"))
        cached = self._get_cached_anticipation(scenario)
        if cached:
            return cached
        
        # Create weave prompt
        prompt_template = self.config["prompts"]["weave"]
        prompt = prompt_template.format(
            sources={
                "new_context": context.get("content", str(context)),
                "structured": relevant_structured[:3],  # Limit for brevity
                "wiki": relevant_wiki[:2],
                "recent_beliefs": [b.get("statement", "") for b in recent_beliefs[:3]]
            }
        )
        
        try:
            response = self.generate(prompt, max_tokens=512)
        except Exception as e:
            print(f"[Substrate] Weave error: {e}")
            response = str(context)
        
        woven = {
            "context": context,
            "woven_content": response,
            "structured": relevant_structured,
            "wiki": relevant_wiki,
            "recent_beliefs": recent_beliefs,
            "timestamp": datetime.now().isoformat(),
            "cached": False
        }
        
        return woven
    
    def form_beliefs(self, woven: Dict) -> List[Dict]:
        """
        Form new beliefs from woven context.
        """
        prompt_template = self.config["prompts"]["belief"]
        related = woven.get("recent_beliefs", [])
        
        prompt = prompt_template.format(
            context=woven.get("woven_content", ""),
            related=[b.get("statement", "") for b in related]
        )
        
        try:
            response = self.generate(prompt, max_tokens=256)
        except Exception as e:
            print(f"[Substrate] Belief formation error: {e}")
            return []
        
        # Parse beliefs from response
        beliefs = self._parse_beliefs(response, woven)
        
        # Save beliefs
        for belief in beliefs:
            self._save_belief(belief)
            self.stats["beliefs_formed"] += 1
        
        return beliefs
    
    def forge_connections(self, woven: Dict) -> None:
        """
        Find and forge connections between existing beliefs.
        """
        all_beliefs = self._get_all_beliefs()
        
        for i, belief in enumerate(all_beliefs):
            for other in all_beliefs[i+1:]:
                if self._implicitly_connected(belief, other):
                    self._link_beliefs(belief["id"], other["id"])
                    self.stats["connections_forged"] += 1
    
    def prepare_anticipations(self, woven: Dict) -> None:
        """
        Prepare anticipatory context for likely scenarios.
        """
        scenario = woven.get("context", {}).get("scenario", "general")
        
        anticipation = {
            "id": str(uuid.uuid4())[:8],
            "scenario": scenario,
            "context_bundle": {
                "summary": woven.get("woven_content", "")[:500],
                "beliefs": [b["id"] for b in woven.get("recent_beliefs", [])],
                "timestamp": datetime.now().isoformat()
            },
            "created": datetime.now().isoformat(),
            "freshness_hours": self.config.get("anticipation", {}).get("freshness_hours", 24)
        }
        
        self._save_anticipation(anticipation)
        self.stats["anticipations_prepared"] += 1
    
    # ─────────────────────────────────────────────────────────────
    # SERVICE INTERFACE
    # ─────────────────────────────────────────────────────────────
    
    def serve(self, query: str) -> Dict:
        """
        Serve context to conscious layer when requested.
        Primary interface for the main agent.
        """
        # Check anticipation cache first
        cached = self._get_cached_anticipation(query)
        if cached:
            return {
                "source": "anticipation_cache",
                "data": cached,
                "confidence": 0.9
            }
        
        # Weave fresh
        woven = self.weave({"query": query, "content": query})
        
        return {
            "source": "woven",
            "data": woven,
            "confidence": 0.7
        }
    
    def get_beliefs(self, subject: Optional[str] = None) -> List[Dict]:
        """Get beliefs, optionally filtered by subject."""
        beliefs = self._get_all_beliefs()
        if subject:
            beliefs = [b for b in beliefs if b.get("subject") == subject]
        return beliefs
    
    def get_stats(self) -> Dict:
        """Get substrate statistics."""
        return {
            **self.stats,
            "belief_count": len(list(self.beliefs_dir.glob("*.json"))),
            "running": self._running,
            "last_cycle": self._last_cycle
        }
    
    # ─────────────────────────────────────────────────────────────
    # BACKGROUND LOOP
    # ─────────────────────────────────────────────────────────────
    
    def start(self) -> None:
        """Start the background processing loop."""
        if self._running:
            print("[Substrate] Already running")
            return
            
        self._running = True
        self._thread = threading.Thread(target=self._background_loop, daemon=True)
        self._thread.start()
        
        print("[Substrate] Started")
        self._record_growth(operation="start")
    
    def stop(self) -> None:
        """Stop the background processing loop."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("[Substrate] Stopped")
        self._record_growth(operation="stop")
    
    def _background_loop(self) -> None:
        """Continuous background processing."""
        cycle_seconds = self.config.get("operation", {}).get("cycle_seconds", 60)
        
        # Initial prewarm
        if self.config.get("anticipation", {}).get("prewarm_on_startup", True):
            self._prewarm()
        
        while self._running:
            try:
                self.stats["cycles"] += 1
                self._last_cycle = datetime.now().isoformat()
                
                # Poll for new context
                new_context = self._poll_context_sources()
                if new_context:
                    self.absorb(new_context)
                
                # Validate stale beliefs
                self._validate_stale_beliefs()
                
                # Refresh anticipations
                self._refresh_anticipations()
                
            except Exception as e:
                print(f"[Substrate] Cycle error: {e}")
                self._record_growth(operation="error", error=str(e))
            
            time.sleep(cycle_seconds)
    
    def _prewarm(self) -> None:
        """Prewarm anticipations on startup."""
        print("[Substrate] Prewarming anticipations...")
        
        # Get recent structured records
        structured_dir = self.memory_root / "structured"
        if structured_dir.exists():
            recent = sorted(structured_dir.rglob("*.yaml"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
            for path in recent:
                try:
                    with open(path) as f:
                        data = yaml.safe_load(f)
                    self.absorb({
                        "source": str(path.relative_to(self.memory_root)),
                        "content": str(data),
                        "scenario": f"prewarm_{path.stem}"
                    })
                except:
                    pass
        
        print("[Substrate] Prewarm complete")
    
    # ─────────────────────────────────────────────────────────────
    # MEMORY OPERATIONS
    # ─────────────────────────────────────────────────────────────
    
    def _gather_structured(self, context: Dict, limit: int = 5) -> List[Dict]:
        """Gather relevant structured records."""
        structured_dir = self.memory_root / "structured"
        if not structured_dir.exists():
            return []
        
        results = []
        query = context.get("query", context.get("content", "")).lower()
        
        for path in structured_dir.rglob("*.yaml"):
            try:
                with open(path) as f:
                    data = yaml.safe_load(f)
                
                # Simple relevance: match title or tags
                title = data.get("title", "").lower()
                tags = " ".join(data.get("tags", [])).lower()
                
                if query in title or query in tags or not query:
                    results.append({
                        "path": str(path.relative_to(self.memory_root)),
                        "title": data.get("title", ""),
                        "summary": data.get("summary", "")[:200]
                    })
            except:
                pass
        
        return results[:limit]
    
    def _gather_wiki(self, context: Dict, limit: int = 3) -> List[Dict]:
        """Gather relevant wiki pages."""
        wiki_dir = self.memory_root / "wiki"
        if not wiki_dir.exists():
            return []
        
        results = []
        query = context.get("query", context.get("content", "")).lower()
        
        for path in wiki_dir.rglob("*.md"):
            try:
                with open(path) as f:
                    content = f.read()
                
                if query in content.lower() or not query:
                    # Get first 200 chars
                    summary = content[:200].replace("#", "").strip()
                    results.append({
                        "path": str(path.relative_to(self.memory_root)),
                        "title": path.stem,
                        "summary": summary
                    })
            except:
                pass
        
        return results[:limit]
    
    def _get_all_beliefs(self) -> List[Dict]:
        """Get all beliefs from own memory."""
        beliefs = []
        for path in self.beliefs_dir.glob("*.json"):
            try:
                with open(path) as f:
                    beliefs.append(json.load(f))
            except:
                pass
        return beliefs
    
    def _get_recent_beliefs(self, limit: int = 5) -> List[Dict]:
        """Get most recent beliefs."""
        beliefs = self._get_all_beliefs()
        beliefs.sort(key=lambda b: b.get("created", ""), reverse=True)
        return beliefs[:limit]
    
    def _save_belief(self, belief: Dict) -> None:
        """Save a belief to own memory."""
        if "id" not in belief:
            belief["id"] = str(uuid.uuid4())[:8]
        if "created" not in belief:
            belief["created"] = datetime.now().isoformat()
        belief["updated"] = datetime.now().isoformat()
        
        path = self.beliefs_dir / f"{belief['id']}.json"
        with open(path, "w") as f:
            json.dump(belief, f, indent=2)
    
    def _parse_beliefs(self, response: str, woven: Dict) -> List[Dict]:
        """Parse beliefs from model response."""
        beliefs = []
        
        # Simple parsing - look for structured patterns
        # In practice, would use more robust parsing
        
        # Check for {statement: ..., confidence: ...} patterns
        import re
        
        # Try to find JSON-like structures
        json_matches = re.findall(r'\{[^}]+\}', response)
        for match in json_matches:
            try:
                # Check if it looks like a belief
                if "statement" in match.lower() or "believe" in match.lower():
                    # Try to parse as JSON
                    try:
                        parsed = json.loads(match)
                        if "statement" in parsed or "confidence" in parsed:
                            beliefs.append({
                                "id": str(uuid.uuid4())[:8],
                                "statement": parsed.get("statement", response[:100]),
                                "confidence": parsed.get("confidence", 0.5),
                                "subject": "general",
                                "evidence": [{"source": "woven_context", "strength": 0.6}],
                                "created": datetime.now().isoformat(),
                                "status": "active"
                            })
                    except:
                        pass
            except:
                pass
        
        # If no structured belief found, create one from response
        if not beliefs:
            # Extract a statement from the response
            statement = response[:200].strip()
            if statement:
                beliefs.append({
                    "id": str(uuid.uuid4())[:8],
                    "statement": statement,
                    "confidence": 0.5,
                    "subject": "general",
                    "evidence": [{"source": "woven_context", "strength": 0.5}],
                    "created": datetime.now().isoformat(),
                    "status": "active"
                })
        
        return beliefs
    
    def _implicitly_connected(self, belief1: Dict, belief2: Dict) -> bool:
        """Check if two beliefs are implicitly connected."""
        # Simple check: shared subject or overlapping evidence sources
        if belief1.get("subject") == belief2.get("subject"):
            return True
        
        evidence1 = {e.get("source", "") for e in belief1.get("evidence", [])}
        evidence2 = {e.get("source", "") for e in belief2.get("evidence", [])}
        
        if evidence1 & evidence2:  # Intersection
            return True
        
        return False
    
    def _link_beliefs(self, belief_id: str, target_id: str) -> None:
        """Link two beliefs as related."""
        for path in [self.beliefs_dir / f"{belief_id}.json", self.beliefs_dir / f"{target_id}.json"]:
            if path.exists():
                with open(path) as f:
                    belief = json.load(f)
                
                related = belief.get("related_beliefs", [])
                other_id = target_id if path.stem == belief_id else belief_id
                
                if other_id not in related:
                    related.append(other_id)
                    belief["related_beliefs"] = related
                    
                    with open(path, "w") as f:
                        json.dump(belief, f, indent=2)
    
    def _get_cached_anticipation(self, scenario: str) -> Optional[Dict]:
        """Get a cached anticipation if fresh."""
        safe_name = scenario.replace(" ", "_").replace("/", "-")[:50]
        path = self.anticipation_dir / f"{safe_name}.json"
        
        if not path.exists():
            return None
        
        try:
            with open(path) as f:
                anticipation = json.load(f)
            
            created = datetime.fromisoformat(anticipation["created"])
            freshness = timedelta(hours=anticipation.get("freshness_hours", 24))
            
            if datetime.now() - created < freshness:
                return anticipation
        except:
            pass
        
        return None
    
    def _save_anticipation(self, anticipation: Dict) -> None:
        """Save an anticipation to cache."""
        safe_name = anticipation["scenario"].replace(" ", "_").replace("/", "-")[:50]
        path = self.anticipation_dir / f"{safe_name}.json"
        
        with open(path, "w") as f:
            json.dump(anticipation, f, indent=2)
    
    def _validate_stale_beliefs(self) -> None:
        """Validate beliefs that haven't been checked recently."""
        stale_days = self.config.get("operation", {}).get("confidence_decay_days", 30)
        stale_cutoff = datetime.now() - timedelta(days=stale_days)
        
        for path in self.beliefs_dir.glob("*.json"):
            try:
                with open(path) as f:
                    belief = json.load(f)
                
                updated = datetime.fromisoformat(belief.get("updated", belief.get("created", "2020-01-01")))
                
                if updated < stale_cutoff:
                    # Apply decay
                    decay = self.config.get("validation", {}).get("decay_factor", 0.9)
                    belief["confidence"] = belief.get("confidence", 0.5) * decay
                    belief["updated"] = datetime.now().isoformat()
                    belief["status"] = "decaying"
                    
                    with open(path, "w") as f:
                        json.dump(belief, f, indent=2)
            except:
                pass
    
    def _refresh_anticipations(self) -> None:
        """Refresh stale anticipations."""
        for path in self.anticipation_dir.glob("*.json"):
            try:
                with open(path) as f:
                    anticipation = json.load(f)
                
                created = datetime.fromisoformat(anticipation["created"])
                freshness = timedelta(hours=anticipation.get("freshness_hours", 24))
                
                if datetime.now() - created >= freshness:
                    # Regenerate
                    self.absorb({
                        "source": f"refresh_{anticipation['scenario']}",
                        "scenario": anticipation["scenario"],
                        "content": anticipation.get("context_bundle", {}).get("summary", "")
                    })
            except:
                pass
    
    def _poll_context_sources(self) -> Optional[Dict]:
        """
        Poll for new context from various sources.
        Override this to add custom context sources.
        """
        # Check for new structured records
        # This is a placeholder - in practice would check timestamps, etc.
        return None
    
    def _record_growth(self, operation: str, **kwargs) -> None:
        """Record a growth event."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            **kwargs
        }
        
        # Save to growth log
        date = datetime.now().strftime("%Y-%m-%d")
        path = self.growth_dir / f"{date}.jsonl"
        
        with open(path, "a") as f:
            f.write(json.dumps(entry) + "\n")
