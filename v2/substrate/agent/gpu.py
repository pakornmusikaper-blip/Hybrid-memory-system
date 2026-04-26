"""
GPU Acceleration Module — v2.3

Enables GPU inference for significantly faster substrate operations.
Supports CUDA GPUs with automatic fallback to CPU.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class GPUManager:
    """
    Manages GPU resources and provides device information.
    
    Features:
    - Auto-detect available GPUs
    - Memory estimation
    - Device selection (cuda/cpu)
    - Model placement optimization
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self._cuda_available = None
        self._gpu_info = None
    
    @property
    def cuda_available(self) -> bool:
        """Check if CUDA is available."""
        if self._cuda_available is None:
            try:
                import torch
                self._cuda_available = torch.cuda.is_available()
            except ImportError:
                self._cuda_available = False
        return self._cuda_available
    
    def get_gpu_info(self) -> Dict:
        """Get information about available GPUs."""
        if self._gpu_info is not None:
            return self._gpu_info
        
        self._gpu_info = {
            "cuda_available": self.cuda_available,
            "device_count": 0,
            "current_device": None,
            "devices": []
        }
        
        if not self.cuda_available:
            return self._gpu_info
        
        try:
            import torch
            self._gpu_info["device_count"] = torch.cuda.device_count()
            self._gpu_info["current_device"] = torch.cuda.current_device()
            
            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                self._gpu_info["devices"].append({
                    "id": i,
                    "name": props.name,
                    "total_memory_gb": props.total_memory / (1024**3),
                    "compute_capability": f"{props.major}.{props.minor}"
                })
        except Exception as e:
            logger.warning(f"Failed to get GPU info: {e}")
        
        return self._gpu_info
    
    def select_device(self) -> str:
        """
        Select the best available device based on config and hardware.
        Returns 'cuda' or 'cpu'.
        """
        config_device = self.config.get("runtime", {}).get("device", "auto")
        
        if config_device == "cpu":
            return "cpu"
        
        if config_device == "cuda" and not self.cuda_available:
            logger.warning("CUDA requested but not available, falling back to CPU")
            return "cpu"
        
        if config_device == "auto":
            if self.cuda_available:
                # Check if GPU has enough memory
                gpu_info = self.get_gpu_info()
                if gpu_info["devices"]:
                    device = gpu_info["devices"][0]
                    total_memory = device.get("total_memory_gb", 0)
                    max_memory = self.config.get("runtime", {}).get("max_memory_gb", 4)
                    
                    if total_memory >= max_memory:
                        return "cuda"
                    else:
                        logger.warning(f"GPU memory ({total_memory:.1f}GB) less than requested ({max_memory}GB)")
                        return "cpu"
            return "cpu"
        
        return config_device
    
    def get_optimal_device_map(self, model_size: str = "small") -> Dict:
        """
        Get optimal device map for model placement.
        
        model_size: 'tiny', 'small', 'medium', 'large'
        """
        if not self.cuda_available:
            return {"": "cpu"}
        
        gpu_info = self.get_gpu_info()
        
        if model_size in ["tiny", "small"]:
            # Small models fit on single GPU
            return {"": f"cuda:{gpu_info['current_device']}"}
        
        if model_size == "medium" and gpu_info["device_count"] >= 2:
            # Split across 2 GPUs
            return {
                "": f"cuda:0",
                "lm_head": f"cuda:1"
            }
        
        # Default: single device
        return {"": f"cuda:{gpu_info['current_device']}"}
    
    def estimate_model_memory(self, model_name: str, quantization: str = "none") -> float:
        """
        Estimate model memory requirement in GB.
        
        Based on model size and quantization.
        """
        # Approximate model sizes (in billions of parameters)
        model_sizes = {
            "Qwen/Qwen2-0.5B": 0.5,
            "Qwen/Qwen2-1.5B": 1.5,
            "Qwen/Qwen2-1.8B": 1.8,
            "microsoft/Phi-3-mini-4k-instruct": 3.8,
            "mistralai/Mistral-7B-Instruct-v0.2": 7.0,
        }
        
        params_billions = model_sizes.get(model_name, 1.0)
        
        # Base memory (FP32 = 4 bytes per param)
        base_memory = params_billions * 4
        
        # Quantization overhead
        if quantization == "4-bit":
            # 0.5 bytes per param + overhead
            memory = params_billions * 0.5 + 0.5
        elif quantization == "8-bit":
            memory = params_billions * 1.0 + 0.3
        else:
            # FP16
            memory = params_billions * 2 + 0.5
        
        return memory
    
    def check_memory_available(self, required_gb: float) -> bool:
        """Check if required memory is available."""
        if not self.cuda_available:
            # Check system RAM
            import psutil
            available = psutil.virtual_memory().available / (1024**3)
            return available >= required_gb
        
        import torch
        device = torch.cuda.current_device()
        props = torch.cuda.get_device_properties(device)
        available = props.total_memory / (1024**3)
        
        return available >= required_gb


class QuantizationConfig:
    """
    Manages quantization configuration for optimal performance.
    """
    
    @staticmethod
    def get_config(quantization: str, device: str) -> Optional[Dict]:
        """
        Get quantization config for transformers.
        
        Returns BitsAndBytesConfig dict or None.
        """
        if quantization == "none":
            return None
        
        try:
            from transformers import BitsAndBytesConfig
            
            if quantization == "4-bit":
                return BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype="float16",
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4"
                )
            elif quantization == "8-bit":
                return BitsAndBytesConfig(
                    load_in_8bit=True
                )
        except ImportError:
            logger.warning("bitsandbytes not available, quantization disabled")
        
        return None
    
    @staticmethod
    def get_dtype(quantization: str):
        """Get appropriate dtype for model loading."""
        if quantization != "none":
            return "auto"
        
        try:
            import torch
            return torch.float16
        except ImportError:
            return "auto"


def auto_configure_for_hardware(config: Dict) -> Dict:
    """
    Auto-configure model settings based on available hardware.
    
    Modifies the config dict in-place.
    Returns the modified config.
    """
    gpu_manager = GPUManager(config)
    
    # Auto-detect device
    device = gpu_manager.select_device()
    config["runtime"]["device"] = device
    
    # Auto-select quantization based on device memory
    if device == "cpu":
        # CPU benefits from aggressive quantization
        if config["model"].get("quantization") == "none":
            model_name = config["model"]["name"]
            memory_estimate = gpu_manager.estimate_model_memory(model_name, "none")
            
            if memory_estimate > 8:
                config["model"]["quantization"] = "4-bit"
                logger.info(f"Auto-enabled 4-bit quantization for {model_name}")
    else:
        # GPU can use less quantization
        gpu_info = gpu_manager.get_gpu_info()
        if gpu_info["devices"]:
            device_info = gpu_info["devices"][0]
            total_memory = device_info.get("total_memory_gb", 8)
            
            if total_memory < 6:
                config["model"]["quantization"] = "4-bit"
                logger.info(f"Auto-enabled 4-bit quantization for {total_memory:.1f}GB GPU")
    
    return config
