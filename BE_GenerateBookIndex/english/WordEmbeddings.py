import torch
import torch.nn.functional as F
import re
import numpy as np
import nltk
from nltk.corpus import stopwords
import os
from models import glove # Import the pre-loaded glove model

script_dir = os.path.dirname(os.path.abspath(__file__))
# REMOVED: glove_file = "E:\\\\Resources\\\\Vector\\\\glove.2024.dolma.300d\\\\dolma_300_2024_1.2M.100_combined.txt"
# REMOVED: glove = torchtext.vocab.Vectors(glove_file)

stop_words = stopwords.words("english")

def cos_sim(w1, w2):
    return float(torch.cosine_similarity(glove[w1].unsqueeze(0),
                                   glove[w2].unsqueeze(0)))

def eucli_dist(w1, w2):
    return float(torch.norm(glove[w2] - glove[w1]))

def count(w1, w2):
    cossim = cos_sim(w1, w2)
    euclid = eucli_dist(w1, w2)
    print(f"{w1} & {w2}\nCos = {cossim}\nEucl = {euclid}")

def print_closest_words_eucl(vec, n=5):
    dists = torch.norm(glove.vectors - vec, dim=1) # compute distances to all words
    lst = sorted(enumerate(dists.numpy()), key=lambda x: x[1]) # sort by distance
    for idx, difference in lst[1:n+1]:
        print(glove.itos[idx], difference)

def print_closest_words_cossim(vec, n=5):
    # Compute cosine similarity between input vector and all word vectors
    sims = F.cosine_similarity(glove.vectors, vec.unsqueeze(0), dim=1)
    
    # Sort by similarity (descending order)
    lst = sorted(enumerate(sims.numpy()), key=lambda x: x[1], reverse=True)
    
    # Print the closest words
    for idx, similarity in lst[:n]:
        print(glove.itos[idx], similarity)

def toTokens(text):
    tokens = re.findall(r"\b(\w+)\b", text)
    # for i in range(len(tokens)):
    #     if tokens[i] in stop_words:
    #         del tokens[i]
    for t in tokens[:]: 
        if t in stop_words:
            tokens.remove(t)
    return tokens

# Add cache for sentence vectors
sentence_vector_cache = {}

def count_vectors_average(sentence):
    # Check cache first
    if sentence in sentence_vector_cache:
        return sentence_vector_cache[sentence]
    
    word_list = toTokens(sentence)
    if not word_list:  # Handle empty word list
        result = torch.zeros(glove.dim)
    else:
        vector_list = [glove[word] for word in word_list]
        vector_list_np = [vector.numpy() for vector in vector_list]
        average_vector_np = np.mean(vector_list_np, axis=0)
        result = torch.tensor(average_vector_np)
    
    # Cache the result
    sentence_vector_cache[sentence] = result
    return result

def average_first(text1, text2):
    ave1 = count_vectors_average(text1)
    ave2 = count_vectors_average(text2)

    dist_cos = float(torch.cosine_similarity(ave1.unsqueeze(0), ave2.unsqueeze(0)))
    dist_eucl = float(torch.norm(ave2 - ave1))
    return dist_cos, dist_eucl

def count_CosAvF(text1, text2):
    ave1 = count_vectors_average(text1)
    ave2 = count_vectors_average(text2)
    
    dist_cos = float(torch.cosine_similarity(ave1.unsqueeze(0), ave2.unsqueeze(0)))
    return dist_cos

# Batch processing function for multiple similarity calculations
def batch_count_CosAvF(keyword, titles):
    """
    Calculate cosine similarities between a keyword and multiple titles efficiently.
    Returns list of similarity scores.
    """
    if not titles:
        return []
    
    # Get keyword vector once
    keyword_vector = count_vectors_average(keyword)
    
    # Get title vectors (cached if already computed)
    title_vectors = [count_vectors_average(title) for title in titles]
    
    # Batch calculate similarities
    similarities = []
    for title_vector in title_vectors:
        sim = float(torch.cosine_similarity(keyword_vector.unsqueeze(0), title_vector.unsqueeze(0)))
        similarities.append(sim)
    
    return similarities

def each_then_average(text1, text2):
    tokens1 = toTokens(text1)
    tokens2 = toTokens(text2)
    dists_cossim = []
    dists_eucl = []
    for i in range(len(tokens1)):
        for j in range(len(tokens2)):
            dists_eucl.append(eucli_dist(tokens1[i], tokens2[j]))
            dists_cossim.append(cos_sim(tokens1[i], tokens2[j]))

    np_eucl = np.array(dists_eucl)
    np_cossim = np.array(dists_cossim)

    ave_eucl = np.mean(np_eucl)
    ave_cossim = np.mean(np_cossim)

    return ave_cossim, ave_eucl

# return tokens which doesnt have embeddings
def checkIfHasEmbeddings(tokens):
    doesntHaveEmbeddings = []
    for token in tokens: 
        tokenVec = glove[token]
        if (tokenVec == torch.zeros_like(tokenVec)).all():
            doesntHaveEmbeddings.append(token)

    return doesntHaveEmbeddings