# Indonesian Language Support Setup Guide

This guide will help you set up the system to process Indonesian books and documents.

## Overview

The system has been enhanced to support both Indonesian and English languages with:
- **Language Detection**: Automatically detects the language of your documents
- **Indonesian RAKE**: Modified keyword extraction for Indonesian text
- **Indonesian Word Embeddings**: Uses FastText for Indonesian word vectors
- **Multilingual API**: Supports both languages in the web interface
- **Indonesian Preprocessing**: Uses Sastrawi stemming and comprehensive stopwords

## Installation Steps

### 1. Install Additional Dependencies

```bash
# Install new requirements
pip install -r requirements_indonesian.txt
```

### 2. Download Indonesian FastText Model

The system will automatically download the Indonesian FastText model on first use, but you can manually download it:

```python
import fasttext.util
fasttext.util.download_model('id', if_exists='ignore')
```

### 3. Test the Installation

Run the test script to verify everything is working:

```bash
python test_indonesian.py
```

## Usage

### Option 1: Use the Multilingual API (Recommended)

Replace your existing API with the Indonesian-enabled version:

```bash
# Backup original API
cp api.py api_original.py

# Use Indonesian-enabled API
cp api_indonesian.py api.py

# Start the server
python api.py
```

The API now supports language selection:

- **Auto-detect**: Automatically detects language (default)
- **Indonesian**: Forces Indonesian processing
- **English**: Forces English processing

### Option 2: Use Individual Components

You can also use the Indonesian modules directly:

```python
import MyRAKE_indonesian as MyRAKE
import WordEmbeddings_indonesian as WordEmbeddings

# Process Indonesian text
text = "Buku ini membahas teknologi informasi di Indonesia"
keywords = MyRAKE.all(text, language='indonesian')

# Calculate similarities
similarity = WordEmbeddings.count_CosAvF("teknologi", "informasi", 'indonesian')
```

## API Endpoints

### Generate RAKE (Enhanced)
- **Endpoint**: `/generate-rake`
- **Method**: POST
- **New Parameters**:
  - `language`: "indonesian", "english", or "auto" (default: "auto")

### Language Detection
- **Endpoint**: `/detect-language`
- **Method**: POST
- **Body**: `{"text": "your text here"}`
- **Response**: `{"language": "indonesian"}`

### Supported Languages
- **Endpoint**: `/supported-languages`
- **Method**: GET
- **Response**: List of supported languages

## Language-Specific Features

### Indonesian Support
- **Stopwords**: Sastrawi/NLTK Indonesian stopword list with curated additions
- **Stemming**: Uses Sastrawi stemmer for canonicalization
- **Word Embeddings**: FastText Indonesian model
- **Text Processing**: Handles Indonesian prefixes (di-, ke-, se-, ber-, ter-, me-)
- **Suffix Removal**: Handles common suffixes (-kan, -an, -i, -nya)

### English Support (Backward Compatible)
- All original English functionality preserved
- Uses original GloVe embeddings

## Configuration

### Language Detection
The system uses simple heuristics to detect language:
- Checks for common Indonesian words
- Falls back to English if uncertain

### Customization
You can modify `indonesian_config.py` to:
- Add more Indonesian stopwords
- Adjust language detection thresholds
- Add custom POS tags

## Troubleshooting

### Common Issues

1. **Sastrawi not installed**
   - Ensure `sastrawi` is in your environment: `pip install sastrawi`

2. **FastText model download fails**
   - Check internet connection
   - Manual download: `fasttext.util.download_model('id')`

3. **Poor keyword extraction for Indonesian**
   - Ensure you're using `language='indonesian'` parameter
   - Verify Sastrawi stemmer initializes (check server logs)

4. **Mixed language documents**
   - Use auto-detection for best results
   - Consider preprocessing to separate languages

### Performance
- Indonesian processing is comparable to English
- FastText model adds ~300MB memory usage
- First run downloads models automatically

## Example Results

### Indonesian Text Processing
```python
text = """
Buku ini membahas tentang perkembangan teknologi informasi di Indonesia.
Teknologi informasi telah menjadi bagian penting dalam kehidupan sehari-hari.
"""

keywords = MyRAKE.all(text, language='indonesian')
# Output: {'teknologi informasi': 12.5, 'indonesia': 8.3, 'perkembangan': 6.2, ...}
```

### Language Detection
```python
detect_language("Buku tentang teknologi")  # Returns: 'indonesian'
detect_language("Book about technology")    # Returns: 'english'
```

## Next Steps

1. **Test with your Indonesian books**
2. **Fine-tune parameters** for your specific use case
3. **Add custom stopwords** if needed
4. **Consider domain-specific** word embeddings

## Support

For issues or questions:
1. Check the troubleshooting section
2. Run `test_indonesian.py` to verify setup
3. Review the configuration files
4. Check console output for model download status