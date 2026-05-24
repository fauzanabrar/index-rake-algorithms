import os
import torch

class GloveStub:
    """Minimal stub for GloVe-like access to keep code operational without torchtext.
    - Provides __getitem__ for word vectors (zeros)
    - Provides .vectors tensor for print helpers
    - Provides .itos list and .dim attribute
    """
    def __init__(self, dim=300):
        self.dim = dim
        self.vectors = torch.zeros(1, dim)
        self.itos = [""]

    def __getitem__(self, word):
        # Return zero vector; replace with real loader if available
        return torch.zeros(self.dim)

# Attempt to initialize real embeddings from an environment path if provided
glove = GloveStub(dim=300)

try:
    glove_path = os.environ.get("GLOVE_TXT_PATH")
    if glove_path and os.path.isfile(glove_path):
        # Optional: implement a simple loader for text vectors here in future
        # For now, we keep the stub to avoid heavy dependency and OS-specific paths
        pass
except Exception:
    pass