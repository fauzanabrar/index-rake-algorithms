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

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "./userinput"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def capitalize(index):
    return index[0].upper() + index[1:]

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

            for rakeIdx in rakeIndex:
                rakeMark = rakeIndex[rakeIdx]["rake"]
                
                # compute its mark against the word embeddings
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
                else: # klo kosong (tidak ada judul di page tsb, maka pake last title saja)
                    title_list = []
                    if tmpTitle:
                        title_list.append(tmpTitle)
                    title_list.append(bookTitle)
                    
                    # Batch calculate similarities with language support
                    similarities = CountWordEmb.batch_count_CosAvF(rakeIdx, title_list, language)
                    cosMark = sum(abs(sim) for sim in similarities if not math.isnan(sim))
                
                rakeIndex[rakeIdx]["cos"] = cosMark

                # compute also the point of its capitalization
                capAmnt = MyRAKE.countCapitalLetters(rakeIdx)
                rakeIndex[rakeIdx]["cap"] = capAmnt

                # count the total sum of them (RAKE + cos + cap)
                total = rakeMark + (cosMark*1) + (capAmnt*8)
                rakeIndex[rakeIdx]["total"] = total
            
            # rank based on the total marks
            sortedRakeIndex = dict(sorted(rakeIndex.items(), key=lambda item: item[1]["total"], reverse=True))
            convert_to_list = list(sortedRakeIndex.items())
            totalIndex = len(sortedRakeIndex)
            numberstotake = 20 if totalIndex>20 else totalIndex
            topN = convert_to_list[:numberstotake]
            topNindexes = dict(topN)
            print(f"Page {j} ({language})")
            print(topNindexes)

            for topNindex in topNindexes:
                # Use a direct, case-insensitive check for existence
                lower_topNindex = topNindex.lower()
                if lower_topNindex not in generated_lower:  # O(1) lookup instead of O(n)
                    # Lemmatize the new keyword ONCE
                    new_lemmas = tuple(token.lemma_ for token in spacy_model(topNindex))

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

    TEXT = ""
    for element in SortedGENERATED:
        TEXT += f"{capitalize(element)}, "
        for lengthh, page in enumerate(SortedGENERATED[element]):
            TEXT += f"{page}"
            if lengthh != len(SortedGENERATED[element])-1:
                TEXT += ", "
        TEXT += "\n"

    generatedPath = "generatedFile.docx"
    doc = DocxTemplate("TEMPLATE.docx")
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
        detected_lang = detect_language(text)
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