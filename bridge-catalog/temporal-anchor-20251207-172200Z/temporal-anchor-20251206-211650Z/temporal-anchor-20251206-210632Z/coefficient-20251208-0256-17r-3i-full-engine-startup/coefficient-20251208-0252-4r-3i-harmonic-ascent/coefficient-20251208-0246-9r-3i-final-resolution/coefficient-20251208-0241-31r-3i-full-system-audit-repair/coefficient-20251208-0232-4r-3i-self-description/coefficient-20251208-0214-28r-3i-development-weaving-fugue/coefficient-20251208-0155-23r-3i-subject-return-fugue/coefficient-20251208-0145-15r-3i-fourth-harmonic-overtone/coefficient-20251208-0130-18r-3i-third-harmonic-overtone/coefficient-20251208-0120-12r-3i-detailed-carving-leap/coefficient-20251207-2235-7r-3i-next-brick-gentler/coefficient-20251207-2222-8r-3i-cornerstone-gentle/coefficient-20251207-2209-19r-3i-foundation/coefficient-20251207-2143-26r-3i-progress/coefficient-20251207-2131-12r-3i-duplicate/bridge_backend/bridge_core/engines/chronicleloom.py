"""
ChronicleLoom - Chronicle Weaving Engine
Advanced chronicle data weaving and temporal documentation engine
Extends ChronicleVault with enhanced temporal weaving capabilities
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from ..chroniclevault import ChronicleVault

logger = logging.getLogger(__name__)


class ChronicleLoom(ChronicleVault):
    """
    Chronicle Weaving Engine extending ChronicleVault
    
    The ChronicleLoom provides advanced chronicle weaving capabilities,
    allowing the system to create temporal narratives and interconnected
    story threads from chronicle data.
    
    Key Rituals:
    - weave: Create temporal narrative threads
    - loom_thread: Generate interconnected story paths
    - pattern_detect: Identify recurring chronicle patterns
    """
    
    def __init__(self, retention_days: int = 365, max_records: int = 100000, max_threads: int = 50):
        super().__init__(retention_days=retention_days, max_records=max_records)
        self.max_threads = max_threads
        self.narrative_threads: Dict[str, Dict[str, Any]] = {}
        self.pattern_cache: Dict[str, List[str]] = {}
        logger.info("🧵 ChronicleLoom Engine initialized")
    
    def weave(self, chronicle_ids: List[str], thread_title: str, 
              narrative_type: str = "temporal") -> Dict[str, Any]:
        """
        Weave chronicles into narrative threads
        
        Args:
            chronicle_ids: List of chronicle IDs to weave
            thread_title: Title for the narrative thread
            narrative_type: Type of narrative (temporal, thematic, causal)
            
        Returns:
            Dict containing the woven narrative thread
        """
        if len(self.narrative_threads) >= self.max_threads:
            logger.warning("⚠️ Maximum narrative threads reached")
            return {"error": "Thread limit exceeded"}
        
        thread_id = f"thread_{int(datetime.now(timezone.utc).timestamp() * 1000)}"
        
        # Gather chronicles for weaving
        woven_chronicles = []
        for chronicle_id in chronicle_ids:
            chronicle = self.get_chronicle(chronicle_id)
            if chronicle:
                woven_chronicles.append(chronicle)
        
        # Create narrative thread
        narrative_thread = {
            "thread_id": thread_id,
            "title": thread_title,
            "narrative_type": narrative_type,
            "chronicles": woven_chronicles,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "thread_length": len(woven_chronicles),
            "temporal_span": self._calculate_temporal_span(woven_chronicles),
            "pattern_strength": self._calculate_pattern_strength(woven_chronicles)
        }
        
        self.narrative_threads[thread_id] = narrative_thread
        
        logger.info(f"🧵 Narrative thread '{thread_title}' woven with {len(woven_chronicles)} chronicles")
        
        return narrative_thread
    
    def loom_thread(self, thread_id: str, pattern_type: str = "causal") -> Dict[str, Any]:
        """
        Generate interconnected story paths from existing thread
        
        Args:
            thread_id: ID of existing narrative thread
            pattern_type: Type of pattern to detect (causal, temporal, thematic)
            
        Returns:
            Dict containing interconnected story paths
        """
        if thread_id not in self.narrative_threads:
            return {"error": f"Thread {thread_id} not found"}
        
        thread = self.narrative_threads[thread_id]
        chronicles = thread["chronicles"]
        
        # Generate story paths based on pattern type
        story_paths = []
        if pattern_type == "causal":
            story_paths = self._generate_causal_paths(chronicles)
        elif pattern_type == "temporal":
            story_paths = self._generate_temporal_paths(chronicles)
        elif pattern_type == "thematic":
            story_paths = self._generate_thematic_paths(chronicles)
        
        result = {
            "thread_id": thread_id,
            "pattern_type": pattern_type,
            "story_paths": story_paths,
            "path_count": len(story_paths),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Cache the pattern for future use
        self.pattern_cache[f"{thread_id}_{pattern_type}"] = story_paths
        
        logger.info(f"🔗 Generated {len(story_paths)} story paths for thread {thread_id}")
        
        return result
    
    def pattern_detect(self, pattern_type: str = "recurring", 
                      threshold: float = 0.7) -> List[Dict[str, Any]]:
        """
        Identify recurring chronicle patterns
        
        Args:
            pattern_type: Type of pattern to detect
            threshold: Minimum pattern strength threshold
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        # Analyze all chronicles for patterns
        chronicles = self.list_chronicles()
        
        if pattern_type == "recurring":
            patterns = self._detect_recurring_patterns(chronicles, threshold)
        elif pattern_type == "anomalous":
            patterns = self._detect_anomalous_patterns(chronicles, threshold)
        elif pattern_type == "temporal":
            patterns = self._detect_temporal_patterns(chronicles, threshold)
        
        logger.info(f"🔍 Detected {len(patterns)} {pattern_type} patterns")
        
        return patterns
    
    def get_narrative_threads(self) -> List[Dict[str, Any]]:
        """Get all narrative threads"""
        return list(self.narrative_threads.values())
    
    def get_thread(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get specific narrative thread"""
        return self.narrative_threads.get(thread_id)
    
    def get_loom_metrics(self) -> Dict[str, Any]:
        """Get ChronicleLoom-specific metrics"""
        base_metrics = self.get_metrics()
        
        return {
            **base_metrics,
            "narrative_threads": len(self.narrative_threads),
            "max_threads": self.max_threads,
            "pattern_cache_size": len(self.pattern_cache),
            "avg_thread_length": sum(t.get("thread_length", 0) for t in self.narrative_threads.values()) / max(len(self.narrative_threads), 1)
        }
    
    # Private helper methods
    def _calculate_temporal_span(self, chronicles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate temporal span of chronicles"""
        if not chronicles:
            return {"span_hours": 0, "earliest": None, "latest": None}
        
        timestamps = [c.get("timestamp", "") for c in chronicles if c.get("timestamp")]
        if not timestamps:
            return {"span_hours": 0, "earliest": None, "latest": None}
        
        try:
            parsed_times = [datetime.fromisoformat(ts.replace('Z', '+00:00')) for ts in timestamps]
            earliest = min(parsed_times)
            latest = max(parsed_times)
            span_hours = (latest - earliest).total_seconds() / 3600
            
            return {
                "span_hours": span_hours,
                "earliest": earliest.isoformat(),
                "latest": latest.isoformat()
            }
        except (ValueError, AttributeError):
            return {"span_hours": 0, "earliest": None, "latest": None}
    
    def _calculate_pattern_strength(self, chronicles: List[Dict[str, Any]]) -> float:
        """Calculate pattern strength of chronicles"""
        if len(chronicles) < 2:
            return 0.0
        
        # Simple pattern strength based on common keywords/topics
        all_content = " ".join(c.get("content", "") for c in chronicles)
        words = all_content.lower().split()
        
        if not words:
            return 0.0
        
        # Calculate word frequency and repetition as pattern strength
        word_counts = {}
        for word in words:
            word_counts[word] = word_counts.get(word, 0) + 1
        
        total_words = len(words)
        repeated_words = sum(1 for count in word_counts.values() if count > 1)
        
        return min(repeated_words / total_words, 1.0)
    
    def _generate_causal_paths(self, chronicles: List[Dict[str, Any]]) -> List[str]:
        """Generate causal story paths"""
        paths = []
        for i, chronicle in enumerate(chronicles[:-1]):
            current_title = chronicle.get("title", f"Chronicle {i}")
            next_title = chronicles[i + 1].get("title", f"Chronicle {i + 1}")
            paths.append(f"{current_title} → {next_title}")
        return paths
    
    def _generate_temporal_paths(self, chronicles: List[Dict[str, Any]]) -> List[str]:
        """Generate temporal story paths"""
        sorted_chronicles = sorted(chronicles, key=lambda c: c.get("timestamp", ""))
        paths = []
        for i, chronicle in enumerate(sorted_chronicles):
            timestamp = chronicle.get("timestamp", "Unknown time")
            title = chronicle.get("title", f"Chronicle {i}")
            paths.append(f"[{timestamp}] {title}")
        return paths
    
    def _generate_thematic_paths(self, chronicles: List[Dict[str, Any]]) -> List[str]:
        """Generate thematic story paths"""
        paths = []
        themes = set()
        
        for chronicle in chronicles:
            content = chronicle.get("content", "")
            # Simple thematic extraction based on keywords
            if "mission" in content.lower():
                themes.add("mission")
            if "agent" in content.lower():
                themes.add("agent")
            if "error" in content.lower() or "fail" in content.lower():
                themes.add("challenge")
            if "success" in content.lower() or "complete" in content.lower():
                themes.add("victory")
        
        for theme in themes:
            related_chronicles = [c for c in chronicles if theme in c.get("content", "").lower()]
            if related_chronicles:
                paths.append(f"Theme: {theme} ({len(related_chronicles)} chronicles)")
        
        return paths
    
    def _detect_recurring_patterns(self, chronicles: List[Dict[str, Any]], threshold: float) -> List[Dict[str, Any]]:
        """Detect recurring patterns in chronicles"""
        patterns = []
        
        # Group chronicles by common elements
        title_groups = {}
        for chronicle in chronicles:
            title = chronicle.get("title", "")
            # Group by first word of title
            first_word = title.split()[0] if title.split() else "unknown"
            if first_word not in title_groups:
                title_groups[first_word] = []
            title_groups[first_word].append(chronicle)
        
        # Find groups that exceed threshold
        for group_name, group_chronicles in title_groups.items():
            if len(group_chronicles) >= threshold * len(chronicles):
                patterns.append({
                    "pattern_type": "recurring",
                    "pattern_name": f"Recurring {group_name}",
                    "frequency": len(group_chronicles),
                    "strength": len(group_chronicles) / len(chronicles),
                    "examples": group_chronicles[:3]  # First 3 examples
                })
        
        return patterns
    
    def _detect_anomalous_patterns(self, chronicles: List[Dict[str, Any]], threshold: float) -> List[Dict[str, Any]]:
        """Detect anomalous patterns in chronicles"""
        patterns = []
        
        # Find chronicles with unusual characteristics
        avg_content_length = sum(len(c.get("content", "")) for c in chronicles) / max(len(chronicles), 1)
        
        for chronicle in chronicles:
            content_length = len(chronicle.get("content", ""))
            if content_length > avg_content_length * 2:  # Unusually long content
                patterns.append({
                    "pattern_type": "anomalous",
                    "pattern_name": "Unusually detailed chronicle",
                    "chronicle_id": chronicle.get("chronicle_id"),
                    "anomaly_score": content_length / avg_content_length,
                    "description": f"Content length {content_length} vs average {avg_content_length:.0f}"
                })
        
        return patterns
    
    def _detect_temporal_patterns(self, chronicles: List[Dict[str, Any]], threshold: float) -> List[Dict[str, Any]]:
        """Detect temporal patterns in chronicles"""
        patterns = []
        
        # Group chronicles by time periods
        time_groups = {}
        for chronicle in chronicles:
            timestamp = chronicle.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hour = dt.hour
                    time_period = "morning" if 6 <= hour < 12 else "afternoon" if 12 <= hour < 18 else "evening" if 18 <= hour < 24 else "night"
                    
                    if time_period not in time_groups:
                        time_groups[time_period] = []
                    time_groups[time_period].append(chronicle)
                except ValueError:
                    continue
        
        # Find temporal patterns
        for period, period_chronicles in time_groups.items():
            if len(period_chronicles) >= threshold * len(chronicles):
                patterns.append({
                    "pattern_type": "temporal",
                    "pattern_name": f"High activity in {period}",
                    "frequency": len(period_chronicles),
                    "strength": len(period_chronicles) / len(chronicles),
                    "time_period": period
                })
        
        return patterns