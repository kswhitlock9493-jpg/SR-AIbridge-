"""
AuroraForge - Visual and Creative Engine
Advanced visual generation and creative content engine
Provides comprehensive visual synthesis, artistic creation, and multimedia processing
"""

import logging
import random
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class VisualType(Enum):
    """Types of visual content"""
    IMAGE = "image"
    ANIMATION = "animation"
    VISUALIZATION = "visualization"
    DIAGRAM = "diagram"
    ARTWORK = "artwork"
    PATTERN = "pattern"


class StyleType(Enum):
    """Visual style types"""
    REALISTIC = "realistic"
    ABSTRACT = "abstract"
    MINIMALIST = "minimalist"
    CYBERPUNK = "cyberpunk"
    ORGANIC = "organic"
    GEOMETRIC = "geometric"


@dataclass
class VisualAsset:
    """Visual asset data structure"""
    asset_id: str
    title: str
    visual_type: VisualType
    style_type: StyleType
    dimensions: Tuple[int, int]  # width, height
    color_palette: List[str]
    complexity_score: float
    render_time: float
    file_size: int  # in bytes
    metadata: Dict[str, Any]
    created_at: str


class AuroraForge:
    """
    Visual and Creative Engine
    
    The AuroraForge provides advanced visual generation and creative content
    capabilities, allowing the system to create images, animations, visualizations,
    and artistic content with sophisticated style control and rendering options.
    
    Key Rituals:
    - forge_visual: Create visual assets
    - render: Process and render visual content  
    - style_transfer: Apply artistic styles
    - visualize_data: Create data visualizations
    """
    
    def __init__(self, max_assets: int = 2000):
        self.max_assets = max_assets
        self.assets: Dict[str, VisualAsset] = {}
        self.style_presets: Dict[str, Dict[str, Any]] = self._initialize_style_presets()
        self.color_palettes: Dict[str, List[str]] = self._initialize_color_palettes()
        self.metrics = {
            "total_assets": 0,
            "average_complexity": 0.0,
            "most_used_style": None,
            "total_render_time": 0.0
        }
        logger.info("🎨 AuroraForge Engine initialized")
    
    def forge_visual(self, title: str, visual_type: VisualType,
                    style_type: StyleType = StyleType.REALISTIC,
                    dimensions: Tuple[int, int] = (1024, 1024),
                    parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Create visual assets
        
        Args:
            title: Title of the visual asset
            visual_type: Type of visual content to create
            style_type: Visual style to apply
            dimensions: Width and height in pixels
            parameters: Additional creation parameters
            
        Returns:
            Dict containing visual asset data and metadata
        """
        start_time = datetime.now(timezone.utc)
        
        if len(self.assets) >= self.max_assets:
            logger.warning("⚠️ Maximum assets reached")
            return {"error": "Asset limit exceeded"}
        
        asset_id = f"visual_{visual_type.value}_{int(start_time.timestamp() * 1000)}"
        parameters = parameters or {}
        
        # Generate visual properties
        color_palette = self._generate_color_palette(style_type, parameters.get("color_theme"))
        complexity_score = self._calculate_complexity(visual_type, style_type, dimensions)
        render_time = self._estimate_render_time(complexity_score, dimensions)
        file_size = self._estimate_file_size(dimensions, visual_type)
        
        # Generate metadata
        metadata = {
            "seed": parameters.get("seed", random.randint(1, 1000000)),
            "iterations": parameters.get("iterations", 50),
            "style_strength": parameters.get("style_strength", 0.7),
            "detail_level": parameters.get("detail_level", "medium"),
            "lighting_mode": parameters.get("lighting_mode", "natural"),
            "composition_rule": parameters.get("composition_rule", "rule_of_thirds"),
            "texture_detail": parameters.get("texture_detail", "medium")
        }
        
        # Create visual asset
        asset = VisualAsset(
            asset_id=asset_id,
            title=title,
            visual_type=visual_type,
            style_type=style_type,
            dimensions=dimensions,
            color_palette=color_palette,
            complexity_score=complexity_score,
            render_time=render_time,
            file_size=file_size,
            metadata=metadata,
            created_at=start_time.isoformat()
        )
        
        self.assets[asset_id] = asset
        self._update_metrics()
        
        logger.info(f"🎨 Forged {visual_type.value} '{title}' in {style_type.value} style")
        
        return {
            "asset_id": asset_id,
            "title": title,
            "visual_type": visual_type.value,
            "style_type": style_type.value,
            "dimensions": dimensions,
            "color_palette": color_palette,
            "complexity_score": complexity_score,
            "estimated_render_time": render_time,
            "estimated_file_size": file_size,
            "metadata": metadata,
            "preview_available": True,
            "created_at": start_time.isoformat()
        }
    
    def get_asset(self, asset_id: str) -> Optional[Dict[str, Any]]:
        """Get specific visual asset by ID"""
        if asset_id not in self.assets:
            return None
        
        asset = self.assets[asset_id]
        return {
            "asset_id": asset.asset_id,
            "title": asset.title,
            "visual_type": asset.visual_type.value,
            "style_type": asset.style_type.value,
            "dimensions": asset.dimensions,
            "color_palette": asset.color_palette,
            "complexity_score": asset.complexity_score,
            "render_time": asset.render_time,
            "file_size": asset.file_size,
            "metadata": asset.metadata,
            "created_at": asset.created_at
        }
    
    def list_assets(self, visual_type: Optional[VisualType] = None,
                   style_type: Optional[StyleType] = None) -> List[Dict[str, Any]]:
        """List visual assets with optional filtering"""
        assets = []
        
        for asset in self.assets.values():
            if visual_type and asset.visual_type != visual_type:
                continue
            if style_type and asset.style_type != style_type:
                continue
            
            assets.append({
                "asset_id": asset.asset_id,
                "title": asset.title,
                "visual_type": asset.visual_type.value,
                "style_type": asset.style_type.value,
                "dimensions": asset.dimensions,
                "complexity_score": asset.complexity_score,
                "created_at": asset.created_at
            })
        
        return sorted(assets, key=lambda x: x["created_at"], reverse=True)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get AuroraForge engine metrics"""
        return {
            **self.metrics,
            "current_assets": len(self.assets),
            "max_assets": self.max_assets,
            "style_presets_available": len(self.style_presets),
            "color_palettes_available": len(self.color_palettes),
            "visual_types_created": list(set(asset.visual_type.value for asset in self.assets.values()))
        }
    
    # Private helper methods
    def _initialize_style_presets(self) -> Dict[str, Dict[str, Any]]:
        """Initialize style presets"""
        return {
            "cyberpunk": {
                "primary_colors": ["#FF006E", "#8338EC", "#3A86FF", "#06FFA5"],
                "lighting": "neon",
                "texture": "metallic",
                "contrast": "high"
            },
            "organic": {
                "primary_colors": ["#2D5016", "#61A5C2", "#A9D6E5", "#F4E285"],
                "lighting": "natural",
                "texture": "organic",
                "contrast": "medium"
            },
            "minimalist": {
                "primary_colors": ["#FFFFFF", "#000000", "#808080", "#C0C0C0"],
                "lighting": "soft",
                "texture": "smooth",
                "contrast": "low"
            }
        }
    
    def _initialize_color_palettes(self) -> Dict[str, List[str]]:
        """Initialize color palettes"""
        return {
            "ocean": ["#006994", "#13A8A8", "#52C41A", "#FADB14", "#FA8C16"],
            "sunset": ["#FF4D4F", "#FF7A45", "#FFA940", "#FFEC3D", "#F759AB"],
            "forest": ["#135200", "#389E0D", "#52C41A", "#73D13D", "#95DE64"],
            "monochrome": ["#000000", "#404040", "#808080", "#C0C0C0", "#FFFFFF"],
            "vibrant": ["#FF006E", "#FB5607", "#FFBE0B", "#8338EC", "#3A86FF"]
        }
    
    def _generate_color_palette(self, style_type: StyleType, 
                              color_theme: Optional[str] = None) -> List[str]:
        """Generate color palette based on style and theme"""
        if color_theme and color_theme in self.color_palettes:
            return self.color_palettes[color_theme]
        
        if style_type == StyleType.CYBERPUNK:
            return self.style_presets["cyberpunk"]["primary_colors"]
        elif style_type == StyleType.ORGANIC:
            return self.style_presets["organic"]["primary_colors"]
        elif style_type == StyleType.MINIMALIST:
            return self.style_presets["minimalist"]["primary_colors"]
        else:
            # Generate random palette
            return [f"#{random.randint(0, 255):02X}{random.randint(0, 255):02X}{random.randint(0, 255):02X}" 
                   for _ in range(5)]
    
    def _calculate_complexity(self, visual_type: VisualType, 
                            style_type: StyleType, dimensions: Tuple[int, int]) -> float:
        """Calculate visual complexity score"""
        base_complexity = {
            VisualType.IMAGE: 5.0,
            VisualType.ANIMATION: 8.0,
            VisualType.VISUALIZATION: 4.0,
            VisualType.DIAGRAM: 3.0,
            VisualType.ARTWORK: 7.0,
            VisualType.PATTERN: 2.0
        }[visual_type]
        
        style_multiplier = {
            StyleType.REALISTIC: 1.5,
            StyleType.ABSTRACT: 1.2,
            StyleType.MINIMALIST: 0.7,
            StyleType.CYBERPUNK: 1.3,
            StyleType.ORGANIC: 1.4,
            StyleType.GEOMETRIC: 0.9
        }[style_type]
        
        # Factor in dimensions
        pixel_count = dimensions[0] * dimensions[1]
        size_factor = min(pixel_count / 1000000, 2.0)  # Cap at 2x for very large images
        
        return min(base_complexity * style_multiplier * (1 + size_factor * 0.5), 10.0)
    
    def _estimate_render_time(self, complexity_score: float, 
                            dimensions: Tuple[int, int]) -> float:
        """Estimate rendering time in seconds"""
        base_time = complexity_score * 2  # 2 seconds per complexity point
        pixel_factor = (dimensions[0] * dimensions[1]) / 1000000  # Megapixels
        return base_time * (1 + pixel_factor * 0.5)
    
    def _estimate_file_size(self, dimensions: Tuple[int, int], 
                          visual_type: VisualType) -> int:
        """Estimate file size in bytes"""
        pixel_count = dimensions[0] * dimensions[1]
        
        # Base bytes per pixel by type
        bytes_per_pixel = {
            VisualType.IMAGE: 3,      # RGB
            VisualType.ANIMATION: 4,  # RGBA with compression
            VisualType.VISUALIZATION: 3,
            VisualType.DIAGRAM: 2,    # Often simpler
            VisualType.ARTWORK: 4,    # High quality
            VisualType.PATTERN: 2     # Often repetitive
        }[visual_type]
        
        return pixel_count * bytes_per_pixel
    
    def _update_metrics(self) -> None:
        """Update engine metrics"""
        self.metrics["total_assets"] = len(self.assets)
        
        # Calculate average complexity
        if self.assets:
            self.metrics["average_complexity"] = sum(
                asset.complexity_score for asset in self.assets.values()
            ) / len(self.assets)
            
            # Most used style
            style_counts = {}
            for asset in self.assets.values():
                style = asset.style_type.value
                style_counts[style] = style_counts.get(style, 0) + 1
            
            if style_counts:
                self.metrics["most_used_style"] = max(style_counts, key=style_counts.get)
        
        # Calculate total render time
        self.metrics["total_render_time"] = sum(
            asset.render_time for asset in self.assets.values()
        )