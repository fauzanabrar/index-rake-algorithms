apa saja library yang dipakai?
apa saja function yang ada?
apa yang perlu di download?

**file api.py**

***librarynya*** 
flask dengan jsonify dan cors
os, math, json
spacy
docxtpl

module pdf_helpers, MyRake, TitleofWholeBooks,Pages_to_pagesr, WordEmbeddings

**helper functions**
capitalize index

**code flow**
spacy model load "en_core_web_md"

Flask
Cors

UPLOAD FOLDER = "./userinput"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

routing

server running

**routes**
POST /generate-rake
    --------- PreProcessing -----------
    request json 
    - filePdf (files)
    - judul
    - adaJSON (jenis)

    save pdf with filename of the file pdf

    get json data fron fileJson and save the jsonFIle on upload folder (config app)
    after that that file is open and read as json and get the pages from the json file
    convert the pages to pages range
    < using 2 modules: Pages_to_pagesr and TitleofWholeBooks>
    return the titles and pages_range in 

    pages_range is a list of dictionary that has f, d, l key of every pages

    titles is a list of list of tuple (page_number, title)

    --------- RAKE ALGORITHM -----------
    create a variable name GENERATED as dictionary and tmpTitle as empty string

    looping the pages_range in pages
    using module pdf_helpers to extract the text from a page in savedPDFfile

    using module MyRAKE to get the dictionary with scores for keywords from the page_text, add the result in rakeIndex variable

    loop the rakeIndex     
        create sub level keys to the rakeIndex with name of the key is "rake"
        example: 
        rakeIndex = {
            "candidate keywords": {
                "rake": 8.5
            },
            "minimal supporting evidence": {
                "rake": 8.16
            },
            "linear time": {
                "rake": 4.0
            }
        }

        calculate the cosine similiarity against the word embeddings

        init cosMark variable with 0 value
        check if titles lengths is not 0 then
            loop the length of the titles
                if the last iteration, compare the title with the bookTitle
                    count word embedding of the rakeIdx and the bookTitle
                    check if Cos_AvF is a number then
                        increment the cosMark variable with absolute value of Cos_AvF
                
                if not 
                    <<i dont really understand what happened here but i think it just check if the title is still the same with full title or it was another new title>>
                    if the tmpTitle is not empty then
                        count the word embedding with CosAvF with rakeIdx and tmpTitle
                        and if the result is number then
                            increment the cosMark variable with absolute value of Cos_AvF

        else then
            check tmpTitle is exist and not null then
                count the wordEmbedding CosAvF between rakeIdx and tmpTitle
                and if the result is number then
                    increment the cosMark variable with absolute value of Cos_AvF
            
            count the Cos_AvF between rakeIdx and bookTitle
                and if the result is number then
                    increment the cosMark variable with absolute value of Cos_AvF


        add to the rakeIndex dictionary key for cos with the cosMark value

        count the capital letters of the rakeIdx and assign it to campAmnt variable
        add the capAmnt to the rakeIndex key named cap

        total the sum of the rakeMark + cosMark*1 (with weight 1) + capAmnt*8 (with weight 8) then assing the result in the total variable
        add the total variable value to the rakeIndex key named total
    
    sorted the rakeIndex by the total value in descending order and change that to  dictionary again
    the sortedRakeIndex convert to the list of dictionary
    get the length of the sortedIndex
    get the first 20 (weight 20) of the total index
    create the list that contain the top 20 of the index rank
    convert the topN list to the dictionary
    print the page of working right now
    print the dictionary of the top 20 index

    loop the top 20 index 
        check the topNindex is not in GENERATED.keys() then
            check the index if is has same lemmas then
                check the idx is None or not(it means the lemmas result is false so it is None) then
                    replace the topNindex key with the value to the master dictionary GENERATED
                else
                    add the topNindex key with the value to the master dictionary GENERATED
        
        else if already exist on the GENERATED dictionary then
            get the index from GENERATED dictionary
            compare the sum of the ascii between topNindex and index from GENERATED dictionary, if the ascii is lower then append it to the GENERATED dictionary
                then skip the loop

    sorted GENERATED dictionaries by the first item keys with lower case which is the index and make it to dictionary again

    create empty TEXT string variable

    loop the element on the sorted GENERATED dictionaries
        append the capitalized of the element on Generated dictionary to the TEXT variable

        loop the sorted GENERATED dictionaries element
            append the page of the element to the TEXT variable

            check if the length of the element is not same like the sorted GENERATED dictionaries element then
                append the commas with space ", " to the TEXT variable
            
            append new line to the TEXT variable
    
            
    --------- OUTPUT -----------
    generated the output documents
    create a file of docs "generatedFile.docx"
    get the template "TEMPLATE.docx"
    render the TEXT output to the docs template and save it to the new file

    remove the savedPDFile and savedJSONFile

    send the output documents as response of the api wit as_attachment is True



**file TitleOfWholeBooks.py**
<<Error: fitx not defined>>
oh fitx is from pdf_helpers

maybe this function will open all the page and extract the headings of the book, page by page?

functions:
    getTitleOfPage (recursive)
        get all titles on a page using regex
        return res, prev, prev_sec

        res is a list of tuple (page_number, title)
        [
            (1, "Introduction"),
            (2, "Background"),
            (3, "Methodology"),
            (4, "Results"),
            (5, "Discussion"),
            (6, "Conclusion")
        ]
    
    titleAndPageNumber
        used by api.py
        get the title and page number from result the getTitleOfPage function
        return the title and page number

        return all is 
        [
            [],  # Page 1 had no titles
            [('1.', 'First Chapter')], # Page 2
            [], # Page 3
            [], # Page 4
            [ # Page 5
                ('1.', 'Introduction to the Topic'),
                ('1.1', 'A Brief History'),
                ('1.2', 'Key Concepts')
            ],
            [('2.', 'Second Chapter')], # Page 6
            # ... and so on for pages 7, 8, 9, 10
            ]

**file Pages_to_pagesr.py**
one functions only to convert the pages to pages range

functions
    convert 
        input: pages (i dont know the type)
        output: pages_range ( list of dictionary that has f, d, l key )

        this function maybe change the normal pages to pages range in a list with 3 key dictionary f, d, l

        <<there is something strange in here, i dont know the pages type and why the need to do that>>


**file pdf_helpers.py**

functions:
    replace_ligatures
        so ligatures is some word that has more than one character, like "fi" or "fl" but in some font, it is a single character. so we need to replace it with the correct word.

        using regex pattern to replace re.escape(ligature) to all match ligature replacements dictionary.

    extract_text_with_mupdf
        using fitz (pyMuPDF) library to open pdf path and get the Document file

        get the text of the document and return it with replaced ligatures.


    extract_text_from_a_page
        using fitz (pyMuPDF) library to open pdf path and get the Document file

        get one page of the document and get the text of that page.

        split the text by new line

        get the textTmp as string and replace the ligatures in the textTmp

        <<i dont know why using the endswith :-1 and t + "" with if else>>


**file MyRAKE.py**
This is the algorithm methods of RAKE (Rapid Automatic Keyword Extraction) that created manually. so many functions but the workflow is simple. 

oh on the top of the file, it must ini the spacy_model which is the "en_core_web_md" model. it will be used on other functions on this file.

Not just space but also the nltk download file is here, the download file is averaged_perceptron_tagger

then set the tags_to_avoid and spacy_tags_to_avoid

<<hmm what is the different between tags_to_avoid and spacy_tags_to_avoid>>

**Debug Mode (step-by-step introspection)**
- Use the CLI at `debug/rake_debug_cli.py` to inspect the RAKE pipeline with detailed information.
- Key flags:
  - `--debug` prints a comprehensive report (tokens, filter decisions with reasons, contiguous segments, phrases, word scores, candidates, and final ranked keywords).
  - `--debug-json <path>` writes the full report to a JSON file for later analysis.
  - `--show-steps` shows a lighter view (tokenization and kept/dropped words) in normal mode.
  - `--language auto|indonesian|english`, `--top N`, `--split-mode default|commas|commas_newlines`.

Examples:
- `python debug/rake_debug_cli.py --text "Teknologi informasi berkembang pesat di era globalisasi" --language indonesian --debug --top 15`
- `python debug/rake_debug_cli.py --text-file E:\path\to\sample.txt --language auto --debug --debug-json E:\path\to\report.json`
- `python debug/rake_debug_cli.py --pdf E:\path\to\book.pdf --page 0 --language auto --debug`

Programmatic usage:
- `from indonesian.MyRAKE_indonesian import Rake`
- `rake = Rake(language='auto')`
- `report = rake.debug_analyze_text(text)`  # returns a dict with keys: `tokens`, `filter_decisions`, `segments`, `phrases`, `word_scores`, `candidates`, `ranked`.

Environment-driven debug (logs and step pauses):
- Set `DEBUG=TRUE` to enable detailed logs from RAKE internals.
- Set `RAKE_DEBUG_STEP=TRUE` to pause after each major phase; press Enter to continue.
- Windows PowerShell examples:
  - `$env:DEBUG = 'TRUE'`
  - `$env:RAKE_DEBUG_STEP = 'TRUE'`
  - `python .\debug\rake_debug_cli.py --text "..." --language indonesian --top 10`
- To disable stepping while keeping logs:
  - `$env:RAKE_DEBUG_STEP = 'FALSE'`

Stopwords source selection (Indonesian):
- You can choose which stopwords set RAKE uses for Indonesian.
- Options: `config` (curated built-in), `nltk`, or `sastrawi`.
- Environment: `$env:RAKE_STOPWORDS_SOURCE = 'nltk'`.
- CLI: `--stopwords-source nltk`.
- Examples:
  - `python .\debug\rake_debug_cli.py --text "Teknologi informasi ..." --language indonesian --stopwords-source nltk --debug`
  - `python .\debug\rake_debug_cli.py --pdf E:\book.pdf --page 0 --language indonesian --stopwords-source config`

Stemming on/off (Indonesian API):
- Toggle Sastrawi stemming used for canonicalization in `indonesian/api.py` and `indonesian/api_indonesian.py`.
- Default: enabled if `RAKE_STEMMER_ENABLED` is unset.
- Disable:
  - Windows PowerShell: `$env:RAKE_STEMMER_ENABLED = 'FALSE'`
  - Effect: API skips Sastrawi initialization and uses lowercase tokens for canonicalization.
- Enable explicitly:
  - `$env:RAKE_STEMMER_ENABLED = 'TRUE'`

functions:
    is_symbol_or_greek:
        simple function to check if the string is a symbol or greek letter using using the unicodedata of the character and return GREEK or SIGN or INCREMENT or REPLACEMENT CHAR

    countCapitalLetters:
        simple function to find all A-Z string length using regex so return is int of the length of the capital letters

    countPuncts:
        create empty variable count, adaBukaKurung, ygDalamKurung

        check ifthe string using regex to get - or +, if matched and the len of the string text is lower than 5 then return 3, check again if the string text is not a word, space or hypen and length of the string is lower than 7 then return 3

        check the string matched the f(x) with ignore case. Then return 3

        loop the string enumarate so get the index and character
            check the adaBukaKurungVariable is positive then add char to variable ygDalamKurung 

            check the char "(" or ")" and check the adaBukaKurungVariable is less than 1, then count variable increase to +3 and fi char is "(" then increase the adaBukaKurung +=1

            if char is ")" then reduce the adaBukaKurung -=1 and count -=3
        
        check the string of the text using regex to catch the word inside parenthesis "()"  and length ygDalamKurung < 4 and countCapitalLetters ygDalamKurung less than 2 then return 3

        or if not return count

    countWordFreq:
        using regex to find the word that has boundary word with lowercase letter and count the word frequency.
        loop the the words that find with regex if word is already in wordFreq dictionary then increase it 1, if not create new key with value 1

        return the wordFreq

    splitEachWord:
        just simple split each word with regex pattern that match with word boundary \b word characters + and \b  wor boundary like - (hyphen) but not for ! or _
        example:
            "Hello, world! This is a test."
            will be split to
            ["Hello", "world", "This", "is", "a", "test"]

    splitEachWord_:
        simple split regex without lowering case the text and get the split pattern is . or ,
        example:
            "Hello, world! This is a test."
            will be split to
            ["Hello", "world", "This", "is", "a", "test"]

    splitTextByStopwords_scratch:
        function to split text by stopwords

        init a words list with splitEachWord_ function for text parameter

        create chunks and tmp empty list

        loop words 
            if the word in stopwords or the last character of the word is "." or length of the word is less than 3 then
                check temp list is empty, if empty skip the loop

                if temp not empty add all of he word to chunks list with join with space " "
                reset the temp list again
            
            if not
                just append the word to temp list
        
        check if the temp list is not empty then add all of the word to chunks list with join with space " "

        return the chunks list

    splitatextByTAG_scratch:
        make a doc using spacy_model with the text provided on the parameter.
        create empty variable, chunks, tmp, and i = 0
        
        loop the doc with the len of the doc
            <<hmm is spacy doc have text, tag, and stop by default?>>

            <<hmm is nextchar is space?>>

            check if it is not last character and the nextchar is "-" so combine the "-" with the nextChar if doesnt so create new space

            check again if the nextChar == "-" and the the_tag is not in spacy_tags_to_avoid then combine the word so it can grab the full - word. then continue with step 2+

            check if the tag is in the spacy tags that to avoid or it was a stopwords or the word length just 1 or 2 or 3 and not the uppercase word, or there is a "." on the_word and the first word is not alphabet or digit then
            check the character shouldnbe 3 characters, if 3 characthers so change it to empty
            or if not appends it on chunks and emptied the tmp

            or if all of that checks not captured so just added the word to tmp variable with space " "

            if tmp is empty append it to chunks with space removed

            split each word of the text

            loop the chunks with copy (because removing list that looping is prohibited)

                remove the unwanted chunks that has symbol then continue

                if punctuations is more than 1 or (1 with chunks length is less than equal 5) then remove the chunk

                split the words of the chunk
                looping the spilt word 
                    if eachword not in will_be_in_wordfreqs then 
                        remove the chunk

            return the chunks that has been filtered


    getUniqueKeywordFromCandidates:
        simple function to get unique keyword from candidates.

        create empty list variable uniKeyword
        loop in range of candidates
            split each word of candidate
                loop the split word
                    if that word is not on uniKeyword
                        then append to uni keyword

        return the list of uniKeyword

        this is simple just create list the word that unique word so not duplicated word

    generateCoOccurenceMatrix:
        create n variable from length of the uniqueKeywordFromCandidates
        create matrix n x n with -7 value for the initial value
        example 3 x 3 matrix:
        [
            [-7, -7, -7],
            [-7, -7, -7],
            [-7, -7, -7]
        ]

        create wordFreqs variable from countWordFreq function

        loop the n range of the matrix
            every matrix diagonal will added a value from uniqueKeywordFromCandidates

        loop n range 
            loop n range again
                if diagoanal skip the loop

                if not and the loop is not -7 then 
                    make the mirror of the matrix with index i j = j i
                
                if the current matrix is 7 then
                    make a tmp variable then
                    for loop k for the range of len of cands
                        <<i think this is for calculate the word associations degrees in matrix>>
        
        return the matrix

    countDegreeofScore:
        create a empty dictionary variable of word_degreeScore

        loop the range of the length of uniqueKeywordFromCandidates variable then
            sum of the degree of word from coOccurenceMatrix in current index
            count the wordFrequency (it just get from the diagonal of the word_freqeuncy)
            count degree of score by divide deggree of word with word frequency
            word_degreeScore in current uniqueKeywordFromCandidates in current index is the degree of score

        return the word_degreeScore dictionary

    sum_ascii:
        simple function to sum of the unicode number of the character from the each character on the string text

    removeDuplicationInCands:
        create empty list variable nonDuplCands

        looping th parameter candidates
            if the cand  words is more than 5, skip the loop

            if cand in lowercase not in nonDuplCans member then
                create index iterator or yield variable that increase if the cand and nonDuplicateCands 
                <<i dont know it looks like checking the cands word split and the nonDuplCands word split, and hypen things>>

            if not 
                create an index yield from nonDuplCands if the ndpl and the cands in lower case is the same
                if sum of ascii number on cand less than of sum of nonDuplCands in current index then
                    replace the nonDuplCands in current index with the cand
                    then skip the loop

        return the nonDuplCands lists

    generateFinalScore:
        create a empty dictionary finalScores

        loop th range of the lengh of nonDuplCands list then
            split each word in current index of nonDuplCands
            initialize score to 0
            loop the splitted words then
                increment the score with the degreeScore of the word
            add to the finalScores dictionary with key is the nonDuplCands in current index and value is the score
        
        return the dictionary of finalScores

    all_useSW:
        use rake algoritm with stopwords split 

        get candididates of the keyword using splitTextByStopwords_scratch function with stopwords
        get uniqueKeywordFromCandidates
        make the coOccurenceMatrix
        count the final scores

        then return the sorted finalScores dictionary from high to low scores

    all:
        first get candidate using splitTextByTAG_scratch function
        then get uniqueKeywordFromCandidates
        make the coOccurenceMatrix
        count the finalScores 
        sortedRake return from the finalScores variable from high to lower scores
        make a copy of sortedRake
        if copySrotedRake = 0 then deleted (because it means the word is not usefull) the the sortedRake index 0
        then return the sortedRake


**file WordEmbeddings.py**
file for all word embeddings function, change the word to the number using word2vec model

***library*** 
torch, torchtext, torch.nn.functional
re, numpy, os
nltk, nltk.corpus (stopwords)

***initialize***
get the script_dir variable to the current directory of the script
path of the glove_file
use glove in torchtext.vocab.Vectory with the path of glove file

stopwords variable from nltk.corpus stopwords in english

***functions***
cos_sim:
    return float  value of w1 and w2 after glove and unsquezee and check the similiarity by cosine similiarity

eucli_dist:
    return float value of two words distance using euclidean distance (simple  pythagoras from 2 glove vector of words)

count:
    print the result of the cosine similiarity and euclidian distance of the two words

print_closest_words_eucl:
    get dinstance of all words with dim 1 from glove vectors between vector parameter using torch norm

    sorted the distance by distance

    loop the sorted distance with range of the length item of the list then
        print the index to string of the index in glove vectors with the result of the difference

print_closest_words_cossim:
    use torch cosine similiarity between the glove vectors and vector parameter with unsqueeze to 2D tensor with 1 dimension or the columns

    sorted list similiarity by distance descending

    loop to print the similiarity with the index of the glove vectors

toTokens:
    function to find all boundary word pattern in the text

    loop the tokens that has matched with regex pattern with clone the tokens
        check the token in stopwords or not, if yes remove the token from tokens.
    
    return list tokens that has been removed from stopwords

count_vectors_average:
    function to count the average of the sentence using word2vec model glove and return the tensor of the average

    first tokenize the sentece with functions toTokens

    after that create vector list of the tokens that has embeddings in glove model

    then count the average of the vector list and return the tensor of the average

average_first:
    count two vector average of text1 and text2

    calculate the cosine similiarity of the two average vector
    calculate the euclidian distance of the two average vector

    return the distance and cosine similiarity of the two average vector

count_CosAvF:
    function to count the cosine similiarity of the two average vector

    create average of 2 text using count_vectors_average function

    <<i dont really understand this>>

    but i think it was using cosine similiarity to get the relation in vector how simmiliar the ave1 and ave2 after unsqueeze to 2D tensor then give the result back to the float number

    return that result in float

each_then_average:
    create two tokens from text1 and text2
    create 2 empty list dists_cossim and dists_eucl
    
    loop the tokens1 length
        loop the tokens2 length
            append the euclidian distance of the tokens1 and tokens2
            append the cosine similiarity of the tokens1 and tokens2

    create np array fro dists_eucl and dists_cossim

    get the average of the dists_eucl and dists_cossim

    return two variables average_eucl and average_cossim

checkIfHasEmbeddings:
    function to check if the tokens has embedding or not using glove  and torch zero like

    create an empty list for tokens that hasnt embeddings

    loop the tokens then
        create vec token with glove
        check if the vec token is same like tensor with same shape of the vec token, if all element is True the result is true then
            add the token to the doesntHaveEmbeddings list

    return the list of doesntHaveEmbeddings
