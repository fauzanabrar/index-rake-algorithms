from flask import Flask, send_file, make_response
from flask import jsonify
from flask import request
from flask_cors import CORS
# Ensure project root is on sys.path for sibling imports when running via script path
import os as _os, sys as _sys
_ROOT_DIR = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _ROOT_DIR not in _sys.path:
    _sys.path.insert(0, _ROOT_DIR)
import pdf_helpers
import os
import json
import Pages_to_pagesr
from tools import TitleOfWholeBooks
from indonesian import MyRAKE_indonesian as MyRAKE
from indonesian import WordEmbeddings_indonesian as CountWordEmb
import math
from docxtpl import DocxTemplate
from indonesian.indonesian_config import detect_language
import re
try:
    from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
    _SASTRAWI_AVAILABLE = True
except Exception:
    _SASTRAWI_AVAILABLE = False

# Environment toggle for stemming (default: enabled if unset)
_env_stem = os.getenv('RAKE_STEMMER_ENABLED', '').strip().lower()
_STEMMER_ENABLED = True if _env_stem == '' else (_env_stem in ('1', 'true', 'yes'))

app = Flask(__name__)
CORS(app)

# Use absolute paths rooted at project directory
UPLOAD_FOLDER = _os.path.join(_ROOT_DIR, "userinput")
_os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def capitalize(index):
    return index[0].upper() + index[1:]

def _collapse_pages(pages):
    s = sorted(set(pages))
    if not s:
        return []
    runs = []
    start = s[0]
    prev = s[0]
    for p in s[1:]:
        if p == prev + 1:
            prev = p
        else:
            runs.append((start, prev))
            start = p
            prev = p
    runs.append((start, prev))
    out = []
    for a, b in runs:
        if a == b:
            out.append(str(a))
        else:
            out.append(f"{a}-{b}")
    return out

def _normalize_term(term):
    t = re.sub(r"[_/\\-]+", " ", term)
    toks = re.findall(r"[A-Za-z]+", t)
    return " ".join(toks).strip()

def _build_index_structure(entries):
    merged = {}
    for term, pages in entries.items():
        norm = _normalize_term(term)
        if not norm:
            continue
        merged.setdefault(norm, [])
        merged[norm].extend(pages)
    heads = {}
    for term in sorted(merged.keys(), key=lambda x: x.lower()):
        toks = re.findall(r"\b\w+\b", term)
        pages = merged[term]
        if len(toks) >= 2 and toks[0] in merged:
            head = toks[0]
            tail = term[len(head):].strip()
            grp = heads.setdefault(head, {"pages": merged.get(head, []), "subs": {}})
            grp["subs"].setdefault(tail, [])
            grp["subs"][tail].extend(pages)
        else:
            grp = heads.setdefault(term, {"pages": [], "subs": {}})
            grp["pages"].extend(pages)
    return heads

def _format_index_text(struct):
    by_letter = {}
    for term in struct:
        letter = term[:1].upper()
        by_letter.setdefault(letter, []).append(term)
    out_lines = []
    for letter in sorted(by_letter.keys()):
        out_lines.append(f"Indeks {letter}")
        for term in sorted(by_letter[letter], key=lambda x: x.lower()):
            info = struct[term]
            pages_fmt = ", ".join(_collapse_pages(info["pages"]))
            if pages_fmt:
                out_lines.append(f"{term} {pages_fmt}")
            else:
                out_lines.append(f"{term}")
            subs = info["subs"]
            for sub in sorted(subs.keys(), key=lambda x: x.lower()):
                spages_fmt = ", ".join(_collapse_pages(subs[sub]))
                out_lines.append(f"- {sub} {spages_fmt}")
    return "\n".join(out_lines)

@app.route('/generate-rake', methods=['POST'])
def generateRake():
    filePDF = request.files["filePdf"]
    bookTitle = request.form.get("judul")
    jenis = request.form.get("adaJSON")
    language = request.form.get("language", "auto")  # auto-detect by default

    if filePDF:
        PDFfilename = filePDF.filename
        savedPDFfile = os.path.join(app.config['UPLOAD_FOLDER'], PDFfilename)
        filePDF.save(savedPDFfile)

    if jenis=="1":
        fileJSON = request.files["fileJson"]
        JSONfilename = fileJSON.filename
        savedJSONfile = os.path.join(app.config['UPLOAD_FOLDER'], JSONfilename)
        fileJSON.save(savedJSONfile)
        with open(savedJSONfile, "r") as jsonFile:
            pages = json.load(jsonFile)
            pages_r = Pages_to_pagesr.convert(pages)
            titles = TitleOfWholeBooks.titleAndPageNumber(pages_r[0]["f"], pages_r[-1]["l"], savedPDFfile, pages_r)

    # Auto-detect language if requested
    if language == "auto":
        # Sample text from first page to detect language
        sample_text = pdf_helpers.extract_text_from_a_page(savedPDFfile, 0)
        language = detect_language(sample_text)
        print(f"Detected language: {language}")

    GENERATED = {}
    lemma_cache = {} # Cache for storing lemmas of already processed keys
    tmpTitle = ""
    # Pre-compute lowercase keys for efficient duplicate checking
    generated_lower = {}  # Maps lowercase keys to original keys

    for i in range(len(pages)):
        for j in range(pages[i]["f"], pages[i]["l"]+1):
            page_text = pdf_helpers.extract_text_from_a_page(savedPDFfile, j+pages[i]["d"]-1)
            rakeIndex = MyRAKE.all(page_text, language=language)

            # Convert RAKE results to expected format with metadata
            formattedRakeIndex = {}
            for keyword, rakeScore in rakeIndex.items():
                formattedRakeIndex[keyword] = {
                    "rake": rakeScore,
                    "cos": 0,  # Will be computed below
                    "cap": 0,  # Will be computed below
                    "total": 0  # Will be computed below
                }

            for rakeIdx in formattedRakeIndex:
                rakeMark = formattedRakeIndex[rakeIdx]["rake"]
                
                cosMark = 0
                if (len(titles[j]) != 0):
                    # Collect all titles for batch processing
                    title_list = []
                    for k in range(len(titles[j]) + 1):
                        if (k == len(titles[j])): # klo iteration trkhr mi, compare ke bookTitle
                            title_list.append(bookTitle)
                        else:
                            tmpTitle = titles[j][k][1] if titles[j][k] else tmpTitle
                            if (tmpTitle != ""):
                                title_list.append(tmpTitle)
                    
                    # Batch calculate similarities with language support
                    similarities = CountWordEmb.batch_count_CosAvF(rakeIdx, title_list, language)
                    cosMark = sum(abs(sim) for sim in similarities if not math.isnan(sim))
                    wn_sims = CountWordEmb.batch_wordnet_similarity(rakeIdx, title_list, language)
                    wnMark = sum(s for s in wn_sims if s is not None)
                else: # klo kosong (tidak ada judul di page tsb, maka pake last title saja)
                    title_list = []
                    if tmpTitle:
                        title_list.append(tmpTitle)
                    title_list.append(bookTitle)
                    
                    # Batch calculate similarities with language support
                    similarities = CountWordEmb.batch_count_CosAvF(rakeIdx, title_list, language)
                    cosMark = sum(abs(sim) for sim in similarities if not math.isnan(sim))
                    wn_sims = CountWordEmb.batch_wordnet_similarity(rakeIdx, title_list, language)
                    wnMark = sum(s for s in wn_sims if s is not None)
                
                formattedRakeIndex[rakeIdx]["cos"] = cosMark
                formattedRakeIndex[rakeIdx]["wn"] = wnMark

                # compute also the point of its capitalization
                capAmnt = MyRAKE.countCapitalLetters(rakeIdx)
                formattedRakeIndex[rakeIdx]["cap"] = capAmnt

                # count the total sum of them (RAKE + cos + cap)
                total = rakeMark + (cosMark*1) + (capAmnt*8) + (wnMark*2)
                formattedRakeIndex[rakeIdx]["total"] = total
            
            # Use the formatted index for further processing and rank based on the total marks
            rakeIndex = formattedRakeIndex
            sortedRakeIndex = dict(sorted(rakeIndex.items(), key=lambda item: item[1]["total"], reverse=True))
            convert_to_list = list(sortedRakeIndex.items())
            totalIndex = len(sortedRakeIndex)
            numberstotake = 20 if totalIndex>20 else totalIndex
            topN = convert_to_list[:numberstotake]
            topNindexes = dict(topN)
            print(f"Page {j} ({language})")
            print(topNindexes)

            # Initialize stemmer lazily when needed, controlled by environment toggle
            stemmer = None
            if language == 'indonesian':
                if not _STEMMER_ENABLED:
                    print("RAKE_STEMMER_ENABLED=FALSE → skipping Sastrawi stemming in API")
                elif _SASTRAWI_AVAILABLE:
                    try:
                        stemmer = StemmerFactory().create_stemmer()
                    except Exception as e:
                        print(f"Warning: Failed to initialize Sastrawi stemmer: {e}")
                        stemmer = None

            for topNindex in topNindexes:
                # Use a direct, case-insensitive check for existence
                lower_topNindex = topNindex.lower()
                if lower_topNindex not in generated_lower:  # O(1) lookup instead of O(n)
                    # Canonicalize keyword: stem Indonesian phrase (if enabled), otherwise lowercase tokens
                    if stemmer is not None and language == 'indonesian':
                        stemmed = stemmer.stem(topNindex)
                        new_lemmas = tuple(re.findall(r"\b\w+\b", stemmed.lower()))
                    else:
                        new_lemmas = tuple(re.findall(r"\b\w+\b", topNindex.lower()))

                    # Check if these lemmas exist in our cache
                    if new_lemmas in lemma_cache:
                        # If they exist, append the page number to the existing canonical keyword
                        existing_key = lemma_cache[new_lemmas]
                        GENERATED[existing_key].append(j)
                    else:
                        # If not, this is a new keyword. Add it to GENERATED and update the cache.
                        GENERATED[topNindex] = [j]
                        lemma_cache[new_lemmas] = topNindex
                        generated_lower[lower_topNindex] = topNindex  # Update the lowercase mapping
                else: # If the exact phrase (case-insensitive) already exists
                    # Find the canonical key
                    existing_key = generated_lower[lower_topNindex]
                    GENERATED[existing_key].append(j)

    SortedGENERATED = dict(sorted(GENERATED.items(), key=lambda item: item[0].lower()))
    index_struct = _build_index_structure(SortedGENERATED)
    TEXT = _format_index_text(index_struct)

    generatedPath = _os.path.join(_ROOT_DIR, "generatedFile.docx")
    doc = DocxTemplate(_os.path.join(_ROOT_DIR, "TEMPLATE.docx"))
    doc.render({"content": TEXT})
    doc.save(generatedPath)

    try:
        os.remove(savedPDFfile)
        os.remove(savedJSONfile)
    except:
        print(f"Failed deleting user files")

    # Send the file as a response
    return send_file(generatedPath, as_attachment=True)

@app.route('/detect-language', methods=['POST'])
def detect_language_endpoint():
    """API endpoint to detect language of uploaded text"""
    text = request.json.get('text', '')
    if text:
        print(f"Debug: Received text: {text[:50]}...")
        detected_lang = detect_language(text)
        print(f"Debug: Detected language: {detected_lang}")
        return jsonify({'language': detected_lang})
    return jsonify({'error': 'No text provided'}), 400

@app.route('/supported-languages', methods=['GET'])
def supported_languages():
    """API endpoint to get supported languages"""
    return jsonify({
        'languages': [
            {'code': 'indonesian', 'name': 'Indonesian'},
            {'code': 'english', 'name': 'English'},
            {'code': 'auto', 'name': 'Auto-detect'}
        ]
    })

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1313)