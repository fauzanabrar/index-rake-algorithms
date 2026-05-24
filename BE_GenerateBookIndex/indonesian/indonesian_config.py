"""Indonesian Language Configuration for RAKE"""

# Prefer Sastrawi or NLTK for Indonesian stopwords; fallback to a static set.
try:
    from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
    _factory = StopWordRemoverFactory()
    _sastrawi_stopwords = set(_factory.get_stop_words())
except Exception:
    _sastrawi_stopwords = set()

try:
    import nltk
    from nltk.corpus import stopwords as _nltk_stopwords
    nltk.download('stopwords', quiet=True)
    _nltk_id_stopwords = set(_nltk_stopwords.words('indonesian'))
except Exception:
    _nltk_id_stopwords = set()

# Additional common Indonesian words to include in stopword list
_BASE_STOPWORDS = {
    'yang', 'dan', 'di', 'dari', 'dengan', 'untuk', 'pada', 'ke', 'oleh', 'sebagai',
    'adalah', 'itu', 'dalam', 'akan', 'juga', 'tidak', 'atau', 'sudah', 'saat', 'oleh',
    'karena', 'kita', 'mereka', 'ini', 'itu', 'saya', 'kamu', 'dia', 'kami', 'kalian',
    'beliau', 'ia', 'aku', 'kau', 'anda', 'sini', 'sana', 'disini', 'disana', 'dimana',
    'kemana', 'kenapa', 'bagaimana', 'berapa', 'siapa', 'apa', 'apakah', 'kah', 'lah',
    'pun', 'tah', 'demi', 'tanpa', 'sejak', 'hingga', 'sampai', 'menuju', 'kepada',
    'antara', 'atas', 'bawah', 'depan', 'belakang', 'sebelah', 'samping', 'sekitar',
    'sepanjang', 'selama', 'setelah', 'sebelum', 'sesudah', 'sambil', 'serta', 'apalagi',
    'bahkan', 'malah', 'justru', 'hanya', 'cuma', 'semua', 'seluruh', 'segala', 'masing',
    'tiap', 'setiap', 'beberapa', 'para', 'sang', 'si', 'tatkala', 'ketika', 'waktu',
    'sewaktu', 'sekalian', 'sekaligus', 'seraya', 'sementara', 'demikian', 'begitu',
    'seperti', 'bagai', 'laksana', 'seakan', 'seolah', 'seolah-olah', 'umpama', 'contoh',
    'misal', 'seumpama', 'semisal', 'bak', 'ibarat', 'daripada', 'ketimbang', 'terhadap',
    'tentang', 'mengenai', 'perihal', 'soal', 'hendak', 'mau', 'ingin', 'supaya', 'agar',
    'biar', 'damai', 'tenteram', 'sentosa', 'aman', 'nyaman', 'tentram', 'sejahtera',
    'makmur', 'kaya', 'berlimpah', 'melimpah', 'ruah', 'berkelimpahan', 'berlimpah-limpah',
    'berkelimpah-ruahan', 'banyak', 'banyaknya', 'jumlahnya', 'jumlah', 'kuantitas', 'volume', 'tuliskan', 'tantangan', 'menyebutkan', 'menuliskan',
    'mengurutkan', 'apabila', 'baru', 'beri', 'bertuliskan', 'cara', 'sesuai', 'andaikata', 'dijelaskan', 'akhir', 
    'kalau', 'kali', 'kasus', 'kira kira', 'paling', 'lainnya', 'lalu', 'lebih', 'memanfaatkan', 'memberikan', 'membutuhkan', 'memikirkan',
    'menambahkan', 'mengurutkan', 'menjalankan', 'menemukan', 'mengaktifkan', 'menyajikan', 'menyediakan',
    'menyelesaikan', 'menyimpan', 'miliki', 'muncul', 'paling', 'perubahan', 'pilih', 
    'rinci', 
}

# Build final Indonesian stopwords set prioritizing Sastrawi, then NLTK, plus base
INDONESIAN_STOPWORDS = (
    _sastrawi_stopwords if _sastrawi_stopwords else (
        _nltk_id_stopwords if _nltk_id_stopwords else set()
    )
) | _BASE_STOPWORDS

# Indonesian POS tags to avoid (simplified for Indonesian)
# Indonesian has different POS tag structure than English
INDONESIAN_TAGS_TO_AVOID = {
    'CC',   # Coordinating conjunction (dan, atau)
    'CD',   # Cardinal number (satu, dua)
    'DT',   # Determiner (ini, itu, tersebut)
    'EX',   # Existential there (ada)
    'IN',   # Preposition/subordinating conjunction (di, ke, dari)
    'MD',   # Modal (akan, boleh, harus)
    'PDT',  # Predeterminer (semua, seluruh)
    'POS',  # Possessive ending (-nya, -ku, -mu)
    'PRP',  # Personal pronoun (saya, kamu, dia)
    'PRP$', # Possessive pronoun (milik, punya)
    'RB',   # Adverb (sudah, telah, juga)
    'RP',   # Particle (lah, kah, pun)
    'TO',   # To (untuk)
    'UH',   # Interjection (hai, oh, ya)
    'WDT',  # Wh-determiner (yang, mana)
    'WP',   # Wh-pronoun (siapa, apa)
    'WP$',  # Possessive wh-pronoun (kepunyaan)
    'WRB',  # Wh-adverb (kapan, dimana, kenapa)
    'SCONJ',# Subordinating conjunction (ketika, karena)
    'AUX',  # Auxiliary verb (telah, sedang, akan)
    'PUNCT' # Punctuation (., ,, !, ?)
}

# Indonesian-specific patterns
INDONESIAN_PATTERNS = {
    'capital_letters': r"[A-Z]",  # Keep same for Indonesian
    'word_boundary': r"\b\w+\b",   # Keep same for word boundaries
    'sentence_endings': r"[.!?]",  # Keep same
    'numbers': r"\d+",             # Keep same
    'affixes': {
        'prefixes': ['di', 'ke', 'se', 'ber', 'ter', 'me', 'mem', 'men', 'meng', 'meny', 'pe', 'pen', 'pem', 'peny', 'peng'],
        'suffixes': ['kan', 'an', 'i', 'nya', 'lah', 'kah', 'tah', 'pun'],
        'infixes': ['el', 'er', 'em', 'in', 'il', 'ar', 'al', 'en', 'il', 'er']
    }
}

# Configuration for different approaches
LANGUAGE_CONFIG = {
    'indonesian': {
        'stopwords': INDONESIAN_STOPWORDS,
        'tags_to_avoid': INDONESIAN_TAGS_TO_AVOID,
        'spacy_model': 'id_core_web_sm',
        'patterns': INDONESIAN_PATTERNS,
        'min_word_length': 3,  # Minimum word length to consider
        'use_stemming': True,   # Whether to use stemming
        'use_stopword_removal': True
    },
    'english': {
        'stopwords': None,  # Will use NLTK English stopwords
        'tags_to_avoid': None,  # Will use existing English tags
        'spacy_model': 'en_core_web_md',
        'patterns': None,  # Will use existing patterns
        'min_word_length': 3,
        'use_stemming': False,
        'use_stopword_removal': True
    }
}

# Language detection helper
def detect_language(text):
    """
    Enhanced language detection based on common words and patterns.
    Returns 'indonesian' or 'english'
    """
    # Extended Indonesian indicators
    indonesian_indicators = {
        'yang', 'dan', 'di', 'dari', 'dengan', 'untuk', 'pada', 'ke', 'oleh', 'sebagai',
        'adalah', 'itu', 'dalam', 'akan', 'juga', 'tidak', 'atau', 'sudah', 'saat', 'oleh',
        'karena', 'kita', 'mereka', 'ini', 'saya', 'kamu', 'dia', 'kami', 'kalian',
        'beliau', 'ia', 'aku', 'kau', 'anda', 'sini', 'sana', 'disini', 'disana',
        'dimana', 'kemana', 'kenapa', 'bagaimana', 'berapa', 'siapa', 'apa',
        'apakah', 'kah', 'lah', 'pun', 'demi', 'tanpa', 'sejak', 'hingga', 'sampai',
        'menuju', 'kepada', 'antara', 'atas', 'bawah', 'depan', 'belakang',
        'sebelah', 'samping', 'sekitar', 'sepanjang', 'selama', 'setelah',
        'sebelum', 'sesudah', 'apalagi', 'bahkan', 'malah', 'justru', 'hanya',
        'cuma', 'semua', 'seluruh', 'segala', 'beberapa', 'para', 'sang',
        'ketika', 'waktu', 'sewaktu', 'seperti', 'bagai', 'laksana', 'seakan',
        'daripada', 'ketimbang', 'terhadap', 'tentang', 'mengenai', 'perihal',
        'soal', 'akan', 'hendak', 'mau', 'ingin', 'supaya', 'agar', 'biar'
    }
    
    # Extended English indicators
    english_indicators = {
        'the', 'and', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'of',
        'for', 'with', 'by', 'from', 'about', 'into', 'through', 'during',
        'before', 'after', 'above', 'below', 'up', 'down', 'out', 'off',
        'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there',
        'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few',
        'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
        'own', 'same', 'so', 'than', 'too', 'very', 'can', 'will', 'just',
        'should', 'now', 'this', 'that', 'these', 'those', 'have', 'has',
        'had', 'been', 'be', 'do', 'does', 'did', 'but', 'or', 'if', 'as'
    }
    
    text_lower = text.lower()
    
    # Count occurrences using exact token matches to avoid substring bias
    import re
    tokens = re.findall(r"\b\w+\b", text_lower)
    indonesian_score = sum(1 for tok in tokens if tok in indonesian_indicators)
    english_score = sum(1 for tok in tokens if tok in english_indicators)
    
    # Check for Indonesian-specific patterns (prefixes and suffixes)
    # Common Indonesian prefixes
    indonesian_prefixes = ['di', 'ke', 'se', 'ber', 'ter', 'me', 'mem', 'men', 'meng', 'meny', 'pe', 'pen', 'pem', 'peny', 'peng', 'per']
    indonesian_suffixes = ['kan', 'an', 'i', 'nya', 'lah', 'kah', 'pun']
    
    words = text_lower.split()
    for word in words:
        # Check prefixes
        for prefix in indonesian_prefixes:
            if word.startswith(prefix) and len(word) > len(prefix) + 2:  # Ensure meaningful word length
                indonesian_score += 0.5
                break
        
        # Check suffixes
        for suffix in indonesian_suffixes:
            if word.endswith(suffix) and len(word) > len(suffix) + 2:
                indonesian_score += 0.5
                break
    
    # If still no clear indicators, check for specific patterns
    if indonesian_score <= english_score:
        # Check for very common Indonesian words that might be missed
        very_common_indonesian = ['buku', 'tahun', 'negara', 'presiden', 'pemerintah', 'ekonomi', 'teknologi', 'informasi', 'berkembang', 'pesat', 'era', 'globalisasi']
        very_common_english = ['book', 'year', 'country', 'president', 'government', 'economy', 'technology', 'information', 'developing', 'rapidly', 'era', 'globalization']
        
        for word in very_common_indonesian:
            if word in text_lower:
                indonesian_score += 3  # Increased weight
                break
                
        for word in very_common_english:
            if word in text_lower:
                english_score += 2
                break
        
        # Additional check for Indonesian-specific word combinations
        indonesian_combinations = ['teknologi informasi', 'ekonomi digital', 'pemerintah indonesia']
        for combo in indonesian_combinations:
            if combo in text_lower:
                indonesian_score += 5  # Increased weight for combinations
                break
    
    return 'indonesian' if indonesian_score > english_score else 'english'