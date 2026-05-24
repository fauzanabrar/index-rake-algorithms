import re
import os
import nltk
from nltk.corpus import stopwords
from .indonesian_config import (
    INDONESIAN_STOPWORDS, 
    INDONESIAN_TAGS_TO_AVOID,
    detect_language
)

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)
nltk.download('stopwords', quiet=True)

class Rake(object):
    """
    Multilingual RAKE implementation supporting Indonesian and English
    """
    
    def __init__(self, language='auto', max_length=10000000, min_length=1, custom_stopwords=None, debug_enabled=None, debug_step=None, stopwords_source=None):
        """
        Initialize RAKE with language support
        
        Args:
            language: 'indonesian', 'english', or 'auto' for automatic detection
            max_length: maximum phrase length
            min_length: minimum phrase length
        """
        self.language = language
        self.max_length = max_length
        self.min_length = min_length
        # Debug configuration (from env or parameters)
        env_debug = os.getenv('DEBUG', '').lower() in ('1', 'true', 'yes')
        env_step = os.getenv('RAKE_DEBUG_STEP', '').lower() in ('1', 'true', 'yes')
        self.debug_enabled = env_debug if debug_enabled is None else bool(debug_enabled)
        self.debug_step = env_step if debug_step is None else bool(debug_step)
        # Stopwords source configuration (Indonesian only): 'config'|'nltk'|'sastrawi'
        env_sw_source = os.getenv('RAKE_STOPWORDS_SOURCE', '').strip().lower()
        self.stopwords_source = stopwords_source or (env_sw_source if env_sw_source in {'config','nltk','sastrawi'} else 'config')
        
        # Skip loading spaCy models to avoid spaCy dependency
        self.nlp_id = None
        self.indonesian_model_available = False
        self.nlp_en = None
        self.english_model_available = False
        
        # Initialize stopwords and POS tags
        self.stopwords_list = []
        self.spacy_tags_to_avoid = []
        self.tags_to_avoid = []
        # Heuristics to prefer noun-like phrases in Indonesian
        self.indonesian_verb_prefixes = {'ber', 'ter', 'me', 'mem', 'men', 'meng', 'meny', 'di', 'ke'}
        self.indonesian_noun_suffixes = {'an', 'asi', 'isasi', 'itas', 'ologi', 'ografi', 'isme', 'ment'}
        # Domain-specific instructional words commonly found in textbooks that shouldn’t be index terms
        self.indonesian_domain_stopwords = {
            'bab','bagian','ayo','buatlah','mencoba','bayangkan','jangan','klik','lakukan','langkah','langsung',
            'membuat','menggunakan','memerlukan','menjadi','merupakan','disajikan','dilakukan','dibuat','diisi','dianalisis',
            'contohnya','misalnya','kalanya','kemudian','sebuah','sebagai','berikut','gambar','file','data','format',
            'pembentuk', 'pembentukannya', 'penyusun', 'penyusunnya', 'penghasil', 'pengatur', 'pembawa', 'penerima',
            'penyebab', 'penghubung', 'pembatas', 'penyaring'
        }
        # Allow caller to inject domain-specific stopwords
        self.custom_stopwords = set(custom_stopwords) if custom_stopwords else set()

    def _debug_log(self, phase, **kwargs):
        """Print debug information if enabled."""
        if not self.debug_enabled:
            return
        print(f"[RAKE DEBUG] Phase: {phase}")
        for k, v in kwargs.items():
            try:
                if isinstance(v, (list, tuple, set)):
                    display = list(v)
                    if len(display) > 10:
                        display = display[:10]
                        print(f"  - {k}: {display} ... (total {len(v)})")
                    else:
                        print(f"  - {k}: {display}")
                elif isinstance(v, dict):
                    items = list(v.items())
                    items.sort(key=lambda x: str(x[0]))
                    if len(items) > 10:
                        items = items[:10]
                        print(f"  - {k}: {items} ... (total {len(v)})")
                    else:
                        print(f"  - {k}: {items}")
                else:
                    print(f"  - {k}: {v}")
            except Exception:
                print(f"  - {k}: <unprintable>")

    def _debug_pause(self, note=""):
        """Pause execution in step mode until user presses Enter."""
        if self.debug_step:
            prompt = f"[RAKE DEBUG] {note} Press Enter to continue (q to quit): " if note else "[RAKE DEBUG] Press Enter to continue (q to quit): "
            try:
                resp = input(prompt)
                if isinstance(resp, str) and resp.strip().lower() in ('q', 'quit', 'exit'):
                    raise KeyboardInterrupt("RAKE debug stepping aborted by user")
            except EOFError:
                # Non-interactive context; ignore stepping
                pass
        
    def _load_language_models(self):
        """No-op: spaCy models are not required for stopwords processing"""
        pass
    
    def _get_language(self, text):
        """Determine language for processing"""
        if self.language == 'auto':
            lang = detect_language(text)
        else:
            lang = self.language
        self._debug_log('get_language', selected_language=lang)
        self._debug_pause('after get_language')
        return lang
    
    def _setup_language_specific(self, language):
        """Setup language-specific parameters"""
        if language == 'indonesian':
            if self.stopwords_source == 'nltk':
                try:
                    self.stopwords_list = set(stopwords.words('indonesian'))
                except Exception:
                    # Fallback to curated config list
                    self.stopwords_list = list(INDONESIAN_STOPWORDS)
            elif self.stopwords_source == 'sastrawi':
                try:
                    from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
                    self.stopwords_list = set([w.lower() for w in StopWordRemoverFactory().get_stop_words()])
                except Exception:
                    self.stopwords_list = list(INDONESIAN_STOPWORDS)
            else:
                self.stopwords_list = list(INDONESIAN_STOPWORDS)
            self.spacy_tags_to_avoid = INDONESIAN_TAGS_TO_AVOID
            self.tags_to_avoid = INDONESIAN_TAGS_TO_AVOID
            self.nlp = self.nlp_id if self.indonesian_model_available else None
        else:  # English
            self.stopwords_list = set(stopwords.words('english'))
            self.spacy_tags_to_avoid = {'CC', 'CD', 'DT', 'EX', 'IN', 'MD', 'PDT', 'POS', 'PRP', 'PRP$', 'RB', 'RP', 'TO', 'UH', 'WDT', 'WP', 'WP$', 'WRB', 'SCONJ', 'AUX', 'PUNCT'}
            self.tags_to_avoid = {'CC', 'CD', 'DT', 'EX', 'IN', 'MD', 'PDT', 'POS', 'PRP', 'PRP$', 'RB', 'RP', 'TO', 'UH', 'WDT', 'WP', 'WP$', 'WRB', 'SCONJ', 'AUX', 'PUNCT'}
            self.nlp = self.nlp_en if self.english_model_available else None
        self._debug_log('setup_language', language=language, stopwords_source=self.stopwords_source, stopwords_count=len(self.stopwords_list))
        self._debug_pause('after setup_language')
    
    def _tokenize_text(self, text, language):
        """Tokenize text based on language"""
        if language == 'indonesian':
            # Indonesian-specific tokenization: Split on punctuation, brackets, math operators, en/em dashes, and spaced hyphens
            delimiters = r'[.!?;:,\(\)\[\]\{\}√+=><\/\n\r\t–—]|\s+-\s*|\s*-\s+'
            sentences = re.split(delimiters, text)
            phrases = []
            for sentence in sentences:
                # Split on common Indonesian conjunctions and punctuation
                sentence_phrases = re.split(r'\b(dan|atau|serta|namun|tetapi|sedangkan)\b', sentence)
                phrases.extend([phrase.strip() for phrase in sentence_phrases if phrase.strip()])
            self._debug_log('tokenize_text', language=language, phrases_count=len(phrases), sample_phrases=phrases[:5])
            self._debug_pause('after tokenize_text')
            return phrases
        else:
            # English tokenization (original)
            sentences = re.split(r'[.!?;]', text)
            phrases = []
            for sentence in sentences:
                sentence_phrases = re.split(r'[,]', sentence)
                phrases.extend([phrase.strip() for phrase in sentence_phrases if phrase.strip()])
            self._debug_log('tokenize_text', language=language, phrases_count=len(phrases), sample_phrases=phrases[:5])
            self._debug_pause('after tokenize_text')
            return phrases

    def _filter_words_in_phrase(self, phrase, language):
        """Apply language-specific filtering to words in a phrase and return filtered words"""
        words = re.findall(r'\b\w+\b', phrase.lower())
        if language == 'indonesian':
            filtered_words = []
            for word in words:
                if self._passes_filter(word):
                    filtered_words.append(word)
            return filtered_words
        else:
            # English filtering (original)
            return [word for word in words if len(word) > 2 and word not in self.stopwords_list]

    def _passes_filter(self, word):
        """Indonesian token filter preferring noun-like terms and excluding instructional verbs"""
        if len(word) <= 2:
            return False
        if word in self.stopwords_list:
            return False
        if word in self.custom_stopwords:
            return False
        if word in self.indonesian_domain_stopwords:
            return False

        # Generalized English loan gerunds/verbs in Indonesian ending in "-ing" (like 'skrining', 'kloning', 'scanning')
        native_ing_words = {
            'dinding', 'kucing', 'piring', 'cacing', 'kambing', 'kepiting', 'tebing', 
            'suling', 'taring', 'keping', 'seruling', 'kuping', 'kancing', 'daging',
            'kuning', 'sering', 'asing', 'penting', 'garing', 'kering', 'ramping', 
            'pening', 'bening', 'hening', 'bising', 'miring', 'giring', 'jaring', 
            'pancing', 'saring', 'tanding', 'banting', 'anting', 'samping', 'damping',
            'ranting', 'genting', 'sinting', 'tengking', 'tuding'
        }
        if word.endswith('ing') and word not in native_ing_words:
            return False

        # Heuristic: treat common verb prefixes as separators unless the word looks nominal
        for prefix in self.indonesian_verb_prefixes:
            if word.startswith(prefix) and len(word) > len(prefix) + 2:
                # If it ends with a noun-like suffix, keep; otherwise exclude
                for suf in self.indonesian_noun_suffixes:
                    if word.endswith(suf):
                        return True
                return False

        # Exclude common Indonesian particles/suffixes embedded as whole words
        for particle in ['lah','kah','pun','tah']:
            if word.endswith(particle) and len(word) > len(particle) + 2:
                return False

        return True
    
    def _generate_candidate_keywords(self, phrases, language):
        """Generate candidate keywords"""
        word_list = []
        
        for phrase in phrases:
            # Use unified filtering helper
            filtered_words = self._filter_words_in_phrase(phrase, language)
            word_list.extend(filtered_words)
        self._debug_log('generate_candidate_keywords', total_words=len(word_list))
        self._debug_pause('after generate_candidate_keywords')
        return word_list

    def _calculate_word_scores(self, phrases, language):
        """Calculate RAKE word scores using per-phrase co-occurrence"""
        word_frequency = {}
        word_degree = {}

        for phrase in phrases:
            filtered_words = self._filter_words_in_phrase(phrase, language)
            phrase_len = len(filtered_words)
            if phrase_len == 0:
                continue
            for word in filtered_words:
                word_frequency[word] = word_frequency.get(word, 0) + 1
                # Standard RAKE Degree: sum of the lengths of all phrases containing the word
                word_degree[word] = word_degree.get(word, 0) + phrase_len

        # Calculate word scores: degree / frequency
        word_score = {}
        for word in word_frequency:
            word_score[word] = word_degree[word] / word_frequency[word]

        # Log top word scores
        try:
            top_scores = sorted(word_score.items(), key=lambda x: x[1], reverse=True)[:10]
        except Exception:
            top_scores = []
        self._debug_log('calculate_word_scores', words=len(word_score), top_scores=top_scores)
        self._debug_pause('after calculate_word_scores')
        return word_score
    
    def _generate_candidate_keyword_scores(self, phrases, word_score, language):
        """Generate candidate keyword scores using contiguous non-stopword segments"""
        keyword_candidates = {}

        for phrase in phrases:
            words = re.findall(r'\b\w+\b', phrase.lower())

            def passes_filter(word):
                if language == 'indonesian':
                    return self._passes_filter(word)
                else:
                    return len(word) > 2 and word not in self.stopwords_list

            # Build contiguous segments of non-stopwords
            current_segment = []
            for word in words:
                if passes_filter(word):
                    current_segment.append(word)
                else:
                    if current_segment:
                        candidate = ' '.join(current_segment)
                        phrase_score = sum(word_score.get(w, 0) for w in current_segment)
                        keyword_candidates[candidate] = phrase_score
                        current_segment = []
            # Flush last segment
            if current_segment:
                candidate = ' '.join(current_segment)
                phrase_score = sum(word_score.get(w, 0) for w in current_segment)
                keyword_candidates[candidate] = phrase_score
        try:
            top_candidates = sorted(keyword_candidates.items(), key=lambda x: x[1], reverse=True)[:10]
        except Exception:
            top_candidates = []
        self._debug_log('generate_candidate_keyword_scores', candidates=len(keyword_candidates), top_candidates=top_candidates)
        self._debug_pause('after generate_candidate_keyword_scores')
        return keyword_candidates
    
    def extract_keywords_from_text(self, text):
        """Extract keywords from text"""
        # Determine language
        language = self._get_language(text)
        self._debug_log('extract_start', text_length=len(text))
        
        # Setup language-specific parameters
        self._setup_language_specific(language)
        
        # Tokenize text
        phrases = self._tokenize_text(text, language)
        
        # Calculate word scores
        word_scores = self._calculate_word_scores(phrases, language)
        
        # Generate candidate keyword scores
        keyword_candidates = self._generate_candidate_keyword_scores(phrases, word_scores, language)
        
        # Store results
        self.keywords = keyword_candidates
        
        # Sort keywords by score
        self.ranked_keywords = sorted(keyword_candidates.items(), key=lambda x: x[1], reverse=True)
        self._debug_log('extract_end', total_keywords=len(self.ranked_keywords), top_ranked=self.ranked_keywords[:10])
        self._debug_pause('after extract_keywords_from_text')
    
    def get_ranked_keywords(self):
        """Get ranked keywords"""
        return self.ranked_keywords
    
    def get_keywords(self, num_keywords=None):
        """Get top keywords"""
        if num_keywords is None:
            return [keyword for keyword, score in self.ranked_keywords]
        return [keyword for keyword, score in self.ranked_keywords[:num_keywords]]

    def _debug_filter_reason(self, word, language):
        w = word.lower()
        if language == 'indonesian':
            if w in self.indonesian_domain_stopwords:
                return 'domain stopword'
            if w in self.custom_stopwords or w in self.stopwords_list:
                return 'stopword'
            if re.match(r'^(meng|meny|men|mem|me|di|ke|se)', w) and re.search(r'(kan|lah)$', w):
                return 'verb (prefix/suffix)'
            if w.endswith('lah'):
                return 'imperative suffix'
            return 'include'
        else:
            if w in self.stopwords_list:
                return 'stopword'
            if len(w) <= 2:
                return 'short token'
            return 'include'

    def debug_analyze_text(self, text, language=None):
        lang = language or self._get_language(text)
        self._setup_language_specific(lang)
        tokens = re.findall(r'\b\w+\b', text.lower())
        decisions = []
        for t in tokens:
            if lang == 'indonesian':
                include = self._passes_filter(t)
            else:
                include = len(t) > 2 and t not in self.stopwords_list
            reason = self._debug_filter_reason(t, lang)
            decisions.append({'token': t, 'include': include, 'reason': reason})
        segments = []
        current = []
        for d in decisions:
            if d['include']:
                current.append(d['token'])
            else:
                if current:
                    segments.append(' '.join(current))
                    current = []
        if current:
            segments.append(' '.join(current))
        phrases = self._tokenize_text(text, lang)
        word_scores = self._calculate_word_scores(phrases, lang)
        candidates = self._generate_candidate_keyword_scores(phrases, word_scores, lang)
        self.extract_keywords_from_text(text)
        ranked = self.get_ranked_keywords()
        return {
            'tokens': tokens,
            'filter_decisions': decisions,
            'segments': segments,
            'phrases': phrases,
            'word_scores': word_scores,
            'candidates': candidates,
            'ranked': ranked,
        }

# For backward compatibility
def all(text, language='auto'):
    """
    Convenience function for backward compatibility
    Returns dictionary of keywords and scores
    """
    rake = Rake(language=language)
    rake.extract_keywords_from_text(text)
    return dict(rake.get_ranked_keywords())

def countCapitalLetters(string):
    """Count the number of capital letters in a string"""
    return sum(1 for char in string if char.isupper())