import torch
import torch.nn.functional as F
import re
import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
import os
from .indonesian_config import LANGUAGE_CONFIG, detect_language

# FastText is optional for now - will use fallback approach
try:
    import fasttext
    import fasttext.util
    FASTTEXT_AVAILABLE = True
except ImportError:
    print("Warning: FastText not available. Using fallback approach for Indonesian word embeddings.")
    FASTTEXT_AVAILABLE = False

# Load models based on language
script_dir = os.path.dirname(os.path.abspath(__file__))

# Try to load Indonesian FastText model (optional)
if FASTTEXT_AVAILABLE:
    try:
        # Download Indonesian FastText model if not exists
        fasttext_model_path = os.path.join(script_dir, 'cc.id.300.bin')
        if not os.path.exists(fasttext_model_path):
            print("Downloading Indonesian FastText model...")
            fasttext.util.download_model('id', if_exists='ignore')
            ft_model_id = fasttext.load_model('cc.id.300.bin')
        else:
            ft_model_id = fasttext.load_model(fasttext_model_path)
        INDONESIAN_MODEL_AVAILABLE = True
    except Exception as e:
        print(f"Warning: Indonesian FastText model not available: {e}")
        ft_model_id = None
        INDONESIAN_MODEL_AVAILABLE = False
else:
    INDONESIAN_MODEL_AVAILABLE = False

# Load English GloVe model (original)
from models import glove as glove_en

# Get stopwords
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
try:
    english_stopwords = set(stopwords.words("english"))
except:
    english_stopwords = set()

# Indonesian stopwords from config
from .indonesian_config import INDONESIAN_STOPWORDS
indonesian_stopwords = INDONESIAN_STOPWORDS

def get_stopwords(language='english'):
    """Get stopwords for specified language"""
    if language == 'indonesian':
        return indonesian_stopwords
    else:
        return english_stopwords

def toTokens(text, language='english'):
    """Tokenize text and remove stopwords based on language"""
    tokens = re.findall(r"\b(\w+)\b", text.lower())
    stopwords_set = get_stopwords(language)
    
    # Indonesian-specific: handle common prefixes and suffixes
    if language == 'indonesian':
        filtered_tokens = []
        for token in tokens:
            # Remove common Indonesian prefixes
            modified = token
            for prefix in ['di', 'ke', 'se', 'ber', 'ter', 'me', 'mem', 'men', 'meng', 'pe', 'pen', 'per', 'ber']:
                if modified.startswith(prefix) and len(modified) > len(prefix) + 2:
                    modified = modified[len(prefix):]
                    break
            
            # Remove common Indonesian suffixes
            for suffix in ['kan', 'an', 'i', 'nya', 'lah', 'kah', 'pun']:
                if modified.endswith(suffix) and len(modified) > len(suffix) + 2:
                    modified = modified[:-len(suffix)]
                    break
            
            if modified not in stopwords_set and len(modified) > 2:
                filtered_tokens.append(modified)
        return filtered_tokens
    else:
        return [token for token in tokens if token not in stopwords_set]

# Add cache for sentence vectors
sentence_vector_cache = {}

def get_word_vector(word, language='english'):
    """Get word vector based on language"""
    if language == 'indonesian' and INDONESIAN_MODEL_AVAILABLE:
        try:
            # Get vector from FastText (handles OOV words)
            return torch.tensor(ft_model_id.get_word_vector(word))
        except:
            # Fallback: return zero vector for unknown words
            return torch.zeros(300)  # FastText uses 300 dimensions
    else:
        # Use English GloVe or fallback approach
        if language == 'indonesian':
            # Fallback for Indonesian: try to get similar English words or use character-based approach
            try:
                # Try direct mapping to English GloVe (many technical terms are similar)
                return glove_en[word]
            except KeyError:
                # Character-based fallback: create a simple vector based on character patterns
                return create_fallback_vector(word, 300)
        else:
            # English: use original GloVe
            try:
                return glove_en[word]
            except KeyError:
                return torch.zeros(glove_en.dim)

def create_fallback_vector(word, dim=300):
    """Create a simple character-based vector for unknown Indonesian words"""
    # Simple character-based encoding
    char_vector = torch.zeros(dim)
    
    # Encode character frequencies and patterns
    for i, char in enumerate(word.lower()[:min(len(word), dim//10)]):
        char_code = ord(char) % 256
        char_vector[i * 10:(i + 1) * 10] = char_code / 255.0
    
    # Add length encoding
    char_vector[-1] = len(word) / 50.0  # Normalize length
    
    return char_vector

def count_vectors_average(sentence, language='english'):
    """Calculate average vector for a sentence"""
    cache_key = f"{sentence}_{language}"
    
    # Check cache first
    if cache_key in sentence_vector_cache:
        return sentence_vector_cache[cache_key]
    
    word_list = toTokens(sentence, language)
    if not word_list:  # Handle empty word list
        if language == 'indonesian':
            result = torch.zeros(300 if INDONESIAN_MODEL_AVAILABLE else glove_en.dim)
        else:
            result = torch.zeros(glove_en.dim)
    else:
        vector_list = [get_word_vector(word, language) for word in word_list]
        vector_list_np = [vector.numpy() for vector in vector_list]
        average_vector_np = np.mean(vector_list_np, axis=0)
        result = torch.tensor(average_vector_np)
    
    # Cache the result
    sentence_vector_cache[cache_key] = result
    return result

def count_CosAvF(text1, text2, language='english'):
    """Calculate cosine similarity between two texts"""
    ave1 = count_vectors_average(text1, language)
    ave2 = count_vectors_average(text2, language)
    
    dist_cos = float(torch.cosine_similarity(ave1.unsqueeze(0), ave2.unsqueeze(0)))
    return dist_cos

# Batch processing function for multiple similarity calculations
def batch_count_CosAvF(keyword, titles, language='english'):
    """
    Calculate cosine similarities between a keyword and multiple titles efficiently.
    Returns list of similarity scores.
    """
    if not titles:
        return []
    
    # Get keyword vector once
    keyword_vector = count_vectors_average(keyword, language)
    
    # Get title vectors (cached if already computed)
    title_vectors = [count_vectors_average(title, language) for title in titles]
    
    # Batch calculate similarities
    similarities = []
    for title_vector in title_vectors:
        sim = float(torch.cosine_similarity(keyword_vector.unsqueeze(0), title_vector.unsqueeze(0)))
        similarities.append(sim)
    
    return similarities

# Multi-language support functions
def multilingual_similarity(text1, text2, lang1=None, lang2=None):
    """Calculate similarity between texts in potentially different languages"""
    if lang1 is None:
        lang1 = detect_language(text1)
    if lang2 is None:
        lang2 = detect_language(text2)
    
    # Use the language of the first text for both (simplified approach)
    # In practice, you might want more sophisticated cross-lingual methods
    return count_CosAvF(text1, text2, lang1)

# Original English-specific functions (for backward compatibility)
def cos_sim(w1, w2):
    return float(torch.cosine_similarity(glove_en[w1].unsqueeze(0), glove_en[w2].unsqueeze(0)))

def eucli_dist(w1, w2):
    return float(torch.norm(glove_en[w2] - glove_en[w1]))

def count(w1, w2):
    cossim = cos_sim(w1, w2)
    euclid = eucli_dist(w1, w2)
    print(f"{w1} & {w2}\nCos = {cossim}\nEucl = {euclid}")

def print_closest_words_eucl(vec, n=5):
    dists = torch.norm(glove_en.vectors - vec, dim=1)
    lst = sorted(enumerate(dists.numpy()), key=lambda x: x[1])
    for idx, difference in lst[1:n+1]:
        print(glove_en.itos[idx], difference)

def print_closest_words_cossim(vec, n=5):
    sims = F.cosine_similarity(glove_en.vectors, vec.unsqueeze(0), dim=1)
    lst = sorted(enumerate(sims.numpy()), key=lambda x: x[1], reverse=True)
    for idx, similarity in lst[:n]:
        print(glove_en.itos[idx], similarity)

def average_first(text1, text2):
    ave1 = count_vectors_average(text1, 'english')
    ave2 = count_vectors_average(text2, 'english')
    dist_cos = float(torch.cosine_similarity(ave1.unsqueeze(0), ave2.unsqueeze(0)))
    dist_eucl = float(torch.norm(ave2 - ave1))
    return dist_cos, dist_eucl

def each_then_average(text1, text2):
    tokens1 = toTokens(text1, 'english')
    tokens2 = toTokens(text2, 'english')
    dists_cossim = []
    dists_eucl = []
    for i in range(len(tokens1)):
        for j in range(len(tokens2)):
            dists_eucl.append(eucli_dist(tokens1[i], tokens2[j]))
            dists_cossim.append(cos_sim(tokens1[i], tokens2[j]))

def _tokenize_simple(text):
    return re.findall(r"\b\w+\b", text.lower())

def _get_synsets(word, language='english'):
    if language == 'indonesian':
        return wn.synsets(word, lang='ind')
    return wn.synsets(word)

def _pairwise_wup_similarity(synsets1, synsets2):
    best = 0.0
    for s1 in synsets1:
        for s2 in synsets2:
            sim = s1.wup_similarity(s2)
            if sim is not None and sim > best:
                best = sim
    return best

def wordnet_similarity(phrase, title, language='english'):
    toks1 = [t for t in _tokenize_simple(phrase) if t not in get_stopwords(language)]
    toks2 = [t for t in _tokenize_simple(title) if t not in get_stopwords(language)]
    if not toks1 or not toks2:
        return 0.0
    syns1 = [ _get_synsets(t, language) for t in toks1 ]
    syns2 = [ _get_synsets(t, language) for t in toks2 ]
    syns1 = [s for s in syns1 if s]
    syns2 = [s for s in syns2 if s]
    if not syns1 or not syns2:
        return 0.0
    bests = []
    for s1 in syns1:
        bests.append(_pairwise_wup_similarity(s1, [ss for s in syns2 for ss in s]))
    if not bests:
        return 0.0
    return float(np.mean(bests))

def batch_wordnet_similarity(keyword, titles, language='english'):
    if not titles:
        return []
    return [wordnet_similarity(keyword, t, language) for t in titles]

    np_eucl = np.array(dists_eucl)
    np_cossim = np.array(dists_cossim)
    ave_eucl = np.mean(np_eucl)
    ave_cossim = np.mean(np_cossim)
    return ave_cossim, ave_eucl

def checkIfHasEmbeddings(tokens):
    doesntHaveEmbeddings = []
    for token in tokens: 
        tokenVec = glove_en[token]
        if (tokenVec == torch.zeros_like(tokenVec)).all():
            doesntHaveEmbeddings.append(token)
    return doesntHaveEmbeddings