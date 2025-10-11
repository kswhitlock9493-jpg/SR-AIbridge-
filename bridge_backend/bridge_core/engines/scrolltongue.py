"""
ScrollTongue - Language Processing Engine
Advanced natural language processing and linguistic analysis engine
Provides comprehensive text analysis, translation, and linguistic pattern recognition
"""

import logging
import re
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class LanguageType(Enum):
    """Supported language types"""
    COMMON = "common"
    TECHNICAL = "technical"
    POETIC = "poetic"
    ANCIENT = "ancient"
    CIPHER = "cipher"
    QUANTUM = "quantum"


class AnalysisType(Enum):
    """Types of linguistic analysis"""
    LEXICAL = "lexical"
    SYNTACTIC = "syntactic"
    SEMANTIC = "semantic"
    PRAGMATIC = "pragmatic"
    PHONETIC = "phonetic"
    SENTIMENT = "sentiment"


@dataclass
class LinguisticScroll:
    """Linguistic document data structure"""
    scroll_id: str
    title: str
    content: str
    language_type: LanguageType
    detected_language: str
    word_count: int
    character_count: int
    complexity_score: float
    created_at: str
    analysis_results: Dict[str, Any]


@dataclass
class TranslationResult:
    """Translation operation result"""
    translation_id: str
    source_text: str
    target_text: str
    source_language: str
    target_language: str
    confidence_score: float
    method: str
    created_at: str


class ScrollTongue:
    """
    Language Processing Engine
    
    The ScrollTongue provides advanced natural language processing capabilities,
    allowing the system to analyze text, perform translations, detect patterns,
    and understand linguistic structures across multiple languages and formats.
    
    Key Rituals:
    - inscribe: Store and analyze text documents
    - translate: Perform language translation
    - analyze: Conduct linguistic analysis
    - pattern_detect: Find linguistic patterns
    
    Autonomy Integration:
    - Publishes language analysis events to genesis.intent
    - Subscribes to autonomy guardrails for safe text processing
    """
    
    def __init__(self, max_scrolls: int = 1000, max_translations: int = 500):
        self.max_scrolls = max_scrolls
        self.max_translations = max_translations
        self.scrolls: Dict[str, LinguisticScroll] = {}
        self.translations: Dict[str, TranslationResult] = {}
        self.language_patterns: Dict[str, List[str]] = {}
        self.vocabulary_cache: Dict[str, Dict[str, int]] = {}
        self.metrics = {
            "total_scrolls": 0,
            "total_translations": 0,
            "languages_detected": 0,
            "patterns_found": 0,
            "average_complexity": 0.0,
            "most_common_language": None
        }
        logger.info("📜 ScrollTongue Engine initialized")
    
    def inscribe(self, title: str, content: str, 
                language_type: LanguageType = LanguageType.COMMON) -> Dict[str, Any]:
        """
        Store and analyze text documents
        
        Args:
            title: Title of the document
            content: Text content to analyze
            language_type: Type/category of language
            
        Returns:
            Dict containing scroll data and initial analysis
        """
        start_time = datetime.utcnow()
        
        if len(self.scrolls) >= self.max_scrolls:
            logger.warning("⚠️ Maximum scrolls reached")
            return {"error": "Scroll limit exceeded"}
        
        scroll_id = f"scroll_{int(start_time.timestamp() * 1000)}"
        
        # Basic text analysis
        word_count = len(content.split())
        character_count = len(content)
        detected_language = self._detect_language(content)
        complexity_score = self._calculate_complexity(content)
        
        # Perform initial linguistic analysis
        analysis_results = {
            "lexical": self._lexical_analysis(content),
            "syntactic": self._syntactic_analysis(content),
            "semantic": self._semantic_analysis(content),
            "sentiment": self._sentiment_analysis(content)
        }
        
        # Create linguistic scroll
        scroll = LinguisticScroll(
            scroll_id=scroll_id,
            title=title,
            content=content,
            language_type=language_type,
            detected_language=detected_language,
            word_count=word_count,
            character_count=character_count,
            complexity_score=complexity_score,
            created_at=start_time.isoformat(),
            analysis_results=analysis_results
        )
        
        self.scrolls[scroll_id] = scroll
        
        # Update vocabulary cache
        self._update_vocabulary_cache(detected_language, content)
        
        # Update metrics
        self._update_metrics()
        
        logger.info(f"📝 Inscribed scroll '{title}' with {word_count} words in {detected_language}")
        
        return {
            "scroll_id": scroll_id,
            "title": title,
            "language_type": language_type.value,
            "detected_language": detected_language,
            "word_count": word_count,
            "character_count": character_count,
            "complexity_score": complexity_score,
            "analysis_summary": {
                "unique_words": analysis_results["lexical"]["unique_words"],
                "sentences": analysis_results["syntactic"]["sentence_count"],
                "sentiment_polarity": analysis_results["sentiment"]["polarity"],
                "key_themes": analysis_results["semantic"]["key_themes"][:3]  # Top 3 themes
            },
            "created_at": start_time.isoformat()
        }
    
    def translate(self, text: str, target_language: str, 
                 source_language: str = "auto", method: str = "neural") -> Dict[str, Any]:
        """
        Perform language translation
        
        Args:
            text: Text to translate
            target_language: Target language code
            source_language: Source language code (auto-detect if "auto")
            method: Translation method (neural, statistical, rule-based)
            
        Returns:
            Dict containing translation results
        """
        start_time = datetime.utcnow()
        
        if len(self.translations) >= self.max_translations:
            # Remove oldest translations
            oldest_translations = sorted(self.translations.items(), 
                                       key=lambda x: x[1].created_at)[:50]
            for trans_id, _ in oldest_translations:
                del self.translations[trans_id]
        
        translation_id = f"trans_{int(start_time.timestamp() * 1000)}"
        
        # Detect source language if auto
        if source_language == "auto":
            source_language = self._detect_language(text)
        
        # Perform translation (simplified simulation)
        translated_text, confidence = self._perform_translation(
            text, source_language, target_language, method
        )
        
        # Create translation result
        translation = TranslationResult(
            translation_id=translation_id,
            source_text=text,
            target_text=translated_text,
            source_language=source_language,
            target_language=target_language,
            confidence_score=confidence,
            method=method,
            created_at=start_time.isoformat()
        )
        
        self.translations[translation_id] = translation
        
        logger.info(f"🌐 Translated text from {source_language} to {target_language}")
        
        return {
            "translation_id": translation_id,
            "source_text": text,
            "translated_text": translated_text,
            "source_language": source_language,
            "target_language": target_language,
            "confidence_score": confidence,
            "method": method,
            "word_count": len(text.split()),
            "created_at": start_time.isoformat()
        }
    
    def analyze(self, scroll_id: str, analysis_type: AnalysisType) -> Dict[str, Any]:
        """
        Conduct detailed linguistic analysis
        
        Args:
            scroll_id: ID of scroll to analyze
            analysis_type: Type of analysis to perform
            
        Returns:
            Dict containing detailed analysis results
        """
        start_time = datetime.utcnow()
        
        if scroll_id not in self.scrolls:
            return {"error": f"Scroll {scroll_id} not found"}
        
        scroll = self.scrolls[scroll_id]
        content = scroll.content
        
        # Perform specific analysis based on type
        if analysis_type == AnalysisType.LEXICAL:
            results = self._detailed_lexical_analysis(content)
        elif analysis_type == AnalysisType.SYNTACTIC:
            results = self._detailed_syntactic_analysis(content)
        elif analysis_type == AnalysisType.SEMANTIC:
            results = self._detailed_semantic_analysis(content)
        elif analysis_type == AnalysisType.PRAGMATIC:
            results = self._pragmatic_analysis(content)
        elif analysis_type == AnalysisType.PHONETIC:
            results = self._phonetic_analysis(content)
        elif analysis_type == AnalysisType.SENTIMENT:
            results = self._detailed_sentiment_analysis(content)
        else:
            return {"error": f"Unknown analysis type: {analysis_type}"}
        
        analysis_result = {
            "scroll_id": scroll_id,
            "analysis_type": analysis_type.value,
            "results": results,
            "analyzed_at": start_time.isoformat()
        }
        
        # Update scroll's analysis results
        scroll.analysis_results[analysis_type.value] = results
        
        logger.info(f"🔍 Performed {analysis_type.value} analysis on scroll {scroll_id}")
        
        return analysis_result
    
    def pattern_detect(self, pattern_type: str = "linguistic", 
                      min_frequency: int = 2) -> List[Dict[str, Any]]:
        """
        Find linguistic patterns across scrolls
        
        Args:
            pattern_type: Type of pattern to detect (linguistic, stylistic, thematic)
            min_frequency: Minimum frequency for pattern detection
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        if pattern_type == "linguistic":
            patterns = self._detect_linguistic_patterns(min_frequency)
        elif pattern_type == "stylistic":
            patterns = self._detect_stylistic_patterns(min_frequency)
        elif pattern_type == "thematic":
            patterns = self._detect_thematic_patterns(min_frequency)
        
        # Store patterns for future reference
        self.language_patterns[pattern_type] = [p["pattern"] for p in patterns]
        
        logger.info(f"🔍 Detected {len(patterns)} {pattern_type} patterns")
        
        return patterns
    
    def get_scroll(self, scroll_id: str) -> Optional[Dict[str, Any]]:
        """Get specific scroll by ID"""
        if scroll_id not in self.scrolls:
            return None
        
        scroll = self.scrolls[scroll_id]
        return {
            "scroll_id": scroll.scroll_id,
            "title": scroll.title,
            "content": scroll.content,
            "language_type": scroll.language_type.value,
            "detected_language": scroll.detected_language,
            "word_count": scroll.word_count,
            "character_count": scroll.character_count,
            "complexity_score": scroll.complexity_score,
            "created_at": scroll.created_at,
            "analysis_results": scroll.analysis_results
        }
    
    def list_scrolls(self, language_type: Optional[LanguageType] = None,
                    language: Optional[str] = None) -> List[Dict[str, Any]]:
        """List scrolls with optional filtering"""
        scrolls = []
        
        for scroll in self.scrolls.values():
            if language_type and scroll.language_type != language_type:
                continue
            if language and scroll.detected_language != language:
                continue
            
            scrolls.append({
                "scroll_id": scroll.scroll_id,
                "title": scroll.title,
                "language_type": scroll.language_type.value,
                "detected_language": scroll.detected_language,
                "word_count": scroll.word_count,
                "complexity_score": scroll.complexity_score,
                "created_at": scroll.created_at
            })
        
        return sorted(scrolls, key=lambda x: x["created_at"], reverse=True)
    
    def get_translations(self, source_language: Optional[str] = None,
                        target_language: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get translation history with optional filtering"""
        translations = []
        
        for translation in self.translations.values():
            if source_language and translation.source_language != source_language:
                continue
            if target_language and translation.target_language != target_language:
                continue
            
            translations.append({
                "translation_id": translation.translation_id,
                "source_language": translation.source_language,
                "target_language": translation.target_language,
                "confidence_score": translation.confidence_score,
                "method": translation.method,
                "created_at": translation.created_at
            })
        
        return sorted(translations, key=lambda x: x["created_at"], reverse=True)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get ScrollTongue engine metrics"""
        return {
            **self.metrics,
            "current_scrolls": len(self.scrolls),
            "max_scrolls": self.max_scrolls,
            "current_translations": len(self.translations),
            "max_translations": self.max_translations,
            "vocabulary_languages": list(self.vocabulary_cache.keys()),
            "pattern_types": list(self.language_patterns.keys())
        }
    
    # Private helper methods
    def _detect_language(self, text: str) -> str:
        """Simple language detection based on character patterns"""
        # Simplified language detection
        if re.search(r'[а-яё]', text.lower()):
            return "russian"
        elif re.search(r'[αβγδεζηθικλμνξπρστυφχψω]', text.lower()):
            return "greek"
        elif re.search(r'[äöüß]', text.lower()):
            return "german"
        elif re.search(r'[àâäéèêëîïôöûüÿç]', text.lower()):
            return "french"
        elif re.search(r'[ñáéíóúü]', text.lower()):
            return "spanish"
        else:
            return "english"  # Default
    
    def _calculate_complexity(self, text: str) -> float:
        """Calculate text complexity score"""
        words = text.split()
        if not words:
            return 0.0
        
        # Simple complexity metrics
        avg_word_length = sum(len(word) for word in words) / len(words)
        unique_words = len(set(words))
        vocab_richness = unique_words / len(words) if words else 0
        
        # Sentence complexity
        sentences = text.split('.')
        avg_sentence_length = len(words) / max(len(sentences), 1)
        
        # Combine metrics (0-10 scale)
        complexity = (
            min(avg_word_length / 10, 1) * 2.5 +  # Word length component
            vocab_richness * 2.5 +                 # Vocabulary richness
            min(avg_sentence_length / 20, 1) * 2.5 # Sentence length component
        ) * 1.33  # Scale to 0-10
        
        return min(complexity, 10.0)
    
    def _lexical_analysis(self, text: str) -> Dict[str, Any]:
        """Basic lexical analysis"""
        words = text.split()
        word_freq = {}
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word:
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        return {
            "total_words": len(words),
            "unique_words": len(word_freq),
            "most_frequent": sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5],
            "average_word_length": sum(len(word) for word in words) / max(len(words), 1)
        }
    
    def _syntactic_analysis(self, text: str) -> Dict[str, Any]:
        """Basic syntactic analysis"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        questions = [s for s in sentences if s.endswith('?')]
        exclamations = [s for s in sentences if s.endswith('!')]
        
        return {
            "sentence_count": len(sentences),
            "question_count": len(questions),
            "exclamation_count": len(exclamations),
            "average_sentence_length": sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
        }
    
    def _semantic_analysis(self, text: str) -> Dict[str, Any]:
        """Basic semantic analysis"""
        # Simple keyword-based theme detection
        themes = {
            "technology": ["computer", "software", "digital", "tech", "algorithm", "system"],
            "science": ["research", "study", "analysis", "theory", "experiment", "data"],
            "business": ["market", "company", "profit", "customer", "strategy", "management"],
            "emotion": ["feel", "happy", "sad", "angry", "love", "hate", "joy", "fear"]
        }
        
        text_lower = text.lower()
        theme_scores = {}
        
        for theme, keywords in themes.items():
            score = sum(text_lower.count(keyword) for keyword in keywords)
            if score > 0:
                theme_scores[theme] = score
        
        return {
            "key_themes": sorted(theme_scores.items(), key=lambda x: x[1], reverse=True),
            "theme_diversity": len(theme_scores),
            "dominant_theme": max(theme_scores.items(), key=lambda x: x[1])[0] if theme_scores else None
        }
    
    def _sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Basic sentiment analysis"""
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "happy", "love", "best"]
        negative_words = ["bad", "terrible", "awful", "horrible", "hate", "worst", "sad", "angry"]
        
        text_lower = text.lower()
        positive_count = sum(text_lower.count(word) for word in positive_words)
        negative_count = sum(text_lower.count(word) for word in negative_words)
        
        total_sentiment_words = positive_count + negative_count
        
        if total_sentiment_words == 0:
            polarity = 0.0
            sentiment = "neutral"
        else:
            polarity = (positive_count - negative_count) / total_sentiment_words
            if polarity > 0.1:
                sentiment = "positive"
            elif polarity < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
        
        return {
            "polarity": polarity,
            "sentiment": sentiment,
            "positive_words": positive_count,
            "negative_words": negative_count
        }
    
    def _update_vocabulary_cache(self, language: str, text: str) -> None:
        """Update vocabulary cache for language"""
        if language not in self.vocabulary_cache:
            self.vocabulary_cache[language] = {}
        
        words = [re.sub(r'[^\w]', '', word.lower()) for word in text.split()]
        for word in words:
            if word:
                self.vocabulary_cache[language][word] = \
                    self.vocabulary_cache[language].get(word, 0) + 1
    
    def _update_metrics(self) -> None:
        """Update engine metrics"""
        self.metrics["total_scrolls"] = len(self.scrolls)
        self.metrics["total_translations"] = len(self.translations)
        self.metrics["languages_detected"] = len(self.vocabulary_cache)
        
        if self.scrolls:
            self.metrics["average_complexity"] = sum(
                s.complexity_score for s in self.scrolls.values()
            ) / len(self.scrolls)
            
            # Most common language
            lang_counts = {}
            for scroll in self.scrolls.values():
                lang = scroll.detected_language
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
            
            if lang_counts:
                self.metrics["most_common_language"] = max(lang_counts, key=lang_counts.get)
    
    def _perform_translation(self, text: str, source_lang: str, 
                           target_lang: str, method: str) -> Tuple[str, float]:
        """Perform translation (simplified simulation)"""
        # This is a simplified simulation of translation
        # In a real implementation, you would use actual translation APIs
        
        if source_lang == target_lang:
            return text, 1.0
        
        # Simple word substitution for demonstration
        word_mappings = {
            "english": {
                "hello": {"spanish": "hola", "french": "bonjour", "german": "hallo"},
                "world": {"spanish": "mundo", "french": "monde", "german": "welt"},
                "good": {"spanish": "bueno", "french": "bon", "german": "gut"},
                "morning": {"spanish": "mañana", "french": "matin", "german": "morgen"}
            }
        }
        
        words = text.lower().split()
        translated_words = []
        successful_translations = 0
        
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if (source_lang in word_mappings and 
                clean_word in word_mappings[source_lang] and
                target_lang in word_mappings[source_lang][clean_word]):
                translated_words.append(word_mappings[source_lang][clean_word][target_lang])
                successful_translations += 1
            else:
                translated_words.append(f"[{clean_word}]")  # Untranslated marker
        
        confidence = successful_translations / max(len(words), 1)
        translated_text = " ".join(translated_words)
        
        return translated_text, confidence
    
    def _detailed_lexical_analysis(self, text: str) -> Dict[str, Any]:
        """Detailed lexical analysis"""
        basic_analysis = self._lexical_analysis(text)
        
        # Additional lexical metrics
        words = text.split()
        word_lengths = [len(word) for word in words]
        
        return {
            **basic_analysis,
            "min_word_length": min(word_lengths) if word_lengths else 0,
            "max_word_length": max(word_lengths) if word_lengths else 0,
            "word_length_variance": sum((l - basic_analysis["average_word_length"]) ** 2 
                                      for l in word_lengths) / max(len(word_lengths), 1)
        }
    
    def _detailed_syntactic_analysis(self, text: str) -> Dict[str, Any]:
        """Detailed syntactic analysis"""
        basic_analysis = self._syntactic_analysis(text)
        
        # Additional syntactic features
        clauses = text.split(',')
        parenthetical = text.count('(')
        quotations = text.count('"') + text.count("'")
        
        return {
            **basic_analysis,
            "clause_count": len(clauses),
            "parenthetical_count": parenthetical,
            "quotation_count": quotations // 2  # Pairs of quotes
        }
    
    def _detailed_semantic_analysis(self, text: str) -> Dict[str, Any]:
        """Detailed semantic analysis"""
        basic_analysis = self._semantic_analysis(text)
        
        # Named entity recognition (simplified)
        entities = {
            "names": re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', text),
            "locations": re.findall(r'\b(?:in|at|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', text),
            "organizations": re.findall(r'\b[A-Z][A-Z\s&]+\b', text)
        }
        
        return {
            **basic_analysis,
            "entities": entities,
            "entity_density": sum(len(v) for v in entities.values()) / max(len(text.split()), 1)
        }
    
    def _pragmatic_analysis(self, text: str) -> Dict[str, Any]:
        """Pragmatic analysis (context and usage)"""
        # Speech act detection
        imperatives = len(re.findall(r'^[A-Z][^.!?]*[!]', text, re.MULTILINE))
        requests = text.lower().count("please") + text.lower().count("could you")
        questions = text.count("?")
        
        return {
            "imperatives": imperatives,
            "requests": requests,
            "questions": questions,
            "politeness_markers": text.lower().count("please") + text.lower().count("thank you"),
            "formality_level": self._calculate_formality(text)
        }
    
    def _phonetic_analysis(self, text: str) -> Dict[str, Any]:
        """Phonetic analysis (sound patterns)"""
        vowels = "aeiouAEIOU"
        consonants = "bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ"
        
        vowel_count = sum(text.count(v) for v in vowels)
        consonant_count = sum(text.count(c) for c in consonants)
        
        # Alliteration detection (simplified)
        words = text.split()
        alliterative_pairs = 0
        for i in range(len(words) - 1):
            if words[i] and words[i+1] and words[i][0].lower() == words[i+1][0].lower():
                alliterative_pairs += 1
        
        return {
            "vowel_count": vowel_count,
            "consonant_count": consonant_count,
            "vowel_consonant_ratio": vowel_count / max(consonant_count, 1),
            "alliterative_pairs": alliterative_pairs,
            "phonetic_density": (vowel_count + consonant_count) / max(len(text), 1)
        }
    
    def _detailed_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Detailed sentiment analysis"""
        basic_analysis = self._sentiment_analysis(text)
        
        # Emotional intensity
        intensifiers = ["very", "extremely", "incredibly", "absolutely", "completely"]
        intensity_score = sum(text.lower().count(word) for word in intensifiers)
        
        # Emotional categories
        emotions = {
            "joy": ["happy", "excited", "thrilled", "delighted"],
            "sadness": ["sad", "depressed", "melancholy", "mournful"],
            "anger": ["angry", "furious", "enraged", "irritated"],
            "fear": ["afraid", "scared", "terrified", "anxious"],
            "surprise": ["surprised", "amazed", "astonished", "shocked"]
        }
        
        emotion_scores = {}
        text_lower = text.lower()
        for emotion, words in emotions.items():
            score = sum(text_lower.count(word) for word in words)
            if score > 0:
                emotion_scores[emotion] = score
        
        return {
            **basic_analysis,
            "intensity_score": intensity_score,
            "emotions": emotion_scores,
            "dominant_emotion": max(emotion_scores.items(), key=lambda x: x[1])[0] if emotion_scores else None
        }
    
    def _calculate_formality(self, text: str) -> str:
        """Calculate formality level of text"""
        formal_markers = ["furthermore", "however", "nevertheless", "therefore", "consequently"]
        informal_markers = ["gonna", "wanna", "yeah", "ok", "cool", "awesome"]
        
        formal_count = sum(text.lower().count(marker) for marker in formal_markers)
        informal_count = sum(text.lower().count(marker) for marker in informal_markers)
        
        if formal_count > informal_count:
            return "formal"
        elif informal_count > formal_count:
            return "informal"
        else:
            return "neutral"
    
    def _detect_linguistic_patterns(self, min_frequency: int) -> List[Dict[str, Any]]:
        """Detect linguistic patterns across scrolls"""
        patterns = []
        
        # Word patterns
        all_words = []
        for scroll in self.scrolls.values():
            words = [re.sub(r'[^\w]', '', word.lower()) for word in scroll.content.split()]
            all_words.extend(words)
        
        word_freq = {}
        for word in all_words:
            if word:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Find frequent patterns
        for word, freq in word_freq.items():
            if freq >= min_frequency and len(word) > 3:
                patterns.append({
                    "pattern_type": "word_frequency",
                    "pattern": word,
                    "frequency": freq,
                    "scrolls_containing": [s.scroll_id for s in self.scrolls.values() 
                                         if word in s.content.lower()]
                })
        
        return sorted(patterns, key=lambda x: x["frequency"], reverse=True)[:20]
    
    def _detect_stylistic_patterns(self, min_frequency: int) -> List[Dict[str, Any]]:
        """Detect stylistic patterns"""
        patterns = []
        
        # Sentence length patterns
        sentence_lengths = []
        for scroll in self.scrolls.values():
            sentences = [s.strip() for s in scroll.content.split('.') if s.strip()]
            lengths = [len(s.split()) for s in sentences]
            sentence_lengths.extend(lengths)
        
        if sentence_lengths:
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            patterns.append({
                "pattern_type": "sentence_length",
                "pattern": f"average_{avg_length:.1f}_words",
                "frequency": len(sentence_lengths),
                "description": f"Average sentence length: {avg_length:.1f} words"
            })
        
        return patterns
    
    def _detect_thematic_patterns(self, min_frequency: int) -> List[Dict[str, Any]]:
        """Detect thematic patterns"""
        patterns = []
        
        # Collect themes from all scrolls
        all_themes = []
        for scroll in self.scrolls.values():
            if "semantic" in scroll.analysis_results:
                themes = scroll.analysis_results["semantic"].get("key_themes", [])
                all_themes.extend([theme[0] for theme in themes])
        
        # Count theme frequencies
        theme_freq = {}
        for theme in all_themes:
            theme_freq[theme] = theme_freq.get(theme, 0) + 1
        
        # Find patterns
        for theme, freq in theme_freq.items():
            if freq >= min_frequency:
                patterns.append({
                    "pattern_type": "thematic",
                    "pattern": theme,
                    "frequency": freq,
                    "scrolls_with_theme": [s.scroll_id for s in self.scrolls.values()
                                          if theme in [t[0] for t in s.analysis_results.get("semantic", {}).get("key_themes", [])]]
                })
        
        return sorted(patterns, key=lambda x: x["frequency"], reverse=True)
    
    async def _publish_to_genesis(self, event_type: str, data: Dict[str, Any]):
        """
        Publish ScrollTongue events to Genesis bus for autonomy integration.
        
        Args:
            event_type: Type of event (analysis, translation, pattern)
            data: Event data
        """
        try:
            from bridge_backend.genesis.bus import genesis_bus
            
            if genesis_bus.is_enabled():
                await genesis_bus.publish("genesis.intent", {
                    "type": f"scrolltongue.{event_type}",
                    "source": "scrolltongue",
                    "data": data,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })
        except Exception as e:
            # Silently fail if genesis bus not available
            logger.debug(f"Failed to publish to genesis: {e}")
        return sorted(patterns, key=lambda x: x["frequency"], reverse=True)