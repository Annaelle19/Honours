from flask import Flask, redirect, url_for, render_template, request, jsonify
import csv
import nltk
from nltk.tokenize import word_tokenize
import re


app = Flask(__name__)

# File paths
patients_file_path = "updated_patient_records.csv"
radlex_file_path = "updated_RADLEX.csv"
radlex_mapping_path = "radlex_mapping.csv"

# Negation cues
NEGATION_CUES = ["no", "denies", "denied", "without", "not", "no evidence", "with no", "negative for", "rule out", "ruled out",
                    "no significant", "no new", "no abnormal", "no suspicious", "absence of", "no signs of", "no sign of",
                       "no symptoms of", "no cause of", "without indication of", "negative", "clear", "clear of"]


RESULTS = ["No records were found. Please try again with a different search criteria."]
RADLEX_DICT = {}
SEARCH_IN_COMPARISON = True
SEARCH_IN_INDICATION = True
SEARCH_IN_FINDINGS = True
SEARCH_IN_IMPRESSION = True


############################################################### #  NEGATION ALGORITHM ################################################################ 
# Break report diagnosis into sentences
def tokenize_sentences(report):
    # Use NLTK's sent_tokenize() function for sentence tokenization
    sentences = nltk.sent_tokenize(report)
    return sentences # List of sentences - [sentence 1, sentence 2, ...]


def remove_punctuation(sentence):
    # Use regular expression to remove punctuation
    sentence_without_punctuation = re.sub(r'[^\w\s]', '', sentence)
    return sentence_without_punctuation


# Check if a sentence is negated
def is_negated(report, UML):
    
    UML_present = False
    is_negated = False
    sentences = tokenize_sentences(report)

    for sentence in sentences:
        # Remove punctiation and tokenize the sentence
        sentence = remove_punctuation(sentence)
        tokens = word_tokenize(sentence)
        # print("tokens: ", tokens)

        # # Perform POS tagging
        # tagged_tokens = pos_tag(tokens)
        # print(tagged_tokens)
        uml_tokens = word_tokenize(remove_punctuation(UML))
        count = 0
        prev_index = -1

        for uml in uml_tokens:
            if uml in tokens:
                index = tokens.index(uml)
                test = uml_tokens.index(uml)
                if uml_tokens.index(uml) == 0:
                    prev_index = index
                    count += 1
                elif index == prev_index + 1:
                    count += 1
                    prev_index = index
                else:
                    count = 0
                    prev_index = -1

        if count == len(uml_tokens):
            UML_present = True
        # Check for negation cues
            for token in tokens:
                if token in NEGATION_CUES:
                    is_negated = True
                    break

    if UML_present and not is_negated:
        return False
    else:
        return True
############################################################### #  NEGATION ALGORITHM END ################################################################

# Load radlex dictionary file which maps every radlex label to its synonym: radlex term - synonym
def load_radlex_mapping():
    global RADLEX_DICT
    radlex_dict = {}

    # Read the CSV file and populate the dictionary
    with open(radlex_mapping_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            preferred_label = row['RadLex Term']
            synonyms = row['Synonym']
            radlex_dict[preferred_label] = synonyms
    RADLEX_DICT = radlex_dict


# Remove duplicate records in the output file
def remove_duplicates(raw_records):
    unique_data = []
    for record in raw_records:
        if record not in unique_data:
            unique_data.append(record)
    return unique_data


def get_synonym(keyword):
    synonym = ""
    if keyword != "":
        if keyword in RADLEX_DICT:
            synonym = RADLEX_DICT[keyword]
        else:
            for key, syn in RADLEX_DICT.items():
                if keyword == syn:
                    synonym = key
    return synonym


def get_keyword_list_some_words(keyword):

    keyword_list = [keyword]

    # Break keyword if it is more than one word
    lst = nltk.word_tokenize(keyword)
    if len(lst) > 1:
        keyword_list += lst

    with open(radlex_file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            preferred_label = row["Preferred.Label"]
            if keyword in word_tokenize(preferred_label) and keyword != "" and preferred_label != "":
                keyword_list.append(preferred_label)

    length = len(keyword_list)
    for i in range(length):
        synonym = get_synonym(keyword_list[i])
        keyword_list.append(synonym)

    # Remove empty strings
    keywords = []
    for item in keyword_list:
        if item != "":
            keywords.append(item)

    #print("keywords: ", keywords)
    return keywords


def get_keyword_list_exact_words(keyword):
    keyword_list = [keyword]
    return keyword_list


def highlight_keywords(text, keyword):
    # Convert the list to a string by joining its elements with spaces
    text_str = " ".join(text)
    # Use regular expression to replace the keywords with <b> tags around them
    highlighted_text = re.sub(r'\b' + re.escape(keyword) + r'\b', f'<b>{keyword}</b>', text_str, flags=re.IGNORECASE)
    return highlighted_text


# Get records based on search criteria
def get_records(pcm_id, article_date, keyword):
    records = []
    global SEARCH_MODE
    global SEARCH_IN_COMPARISON, SEARCH_IN_INDICATION, SEARCH_IN_FINDINGS, SEARCH_IN_IMPRESSION

    if keyword:
        if SEARCH_MODE == 'some':
            keyword_list = get_keyword_list_some_words(keyword)
        else:
            keyword_list = get_keyword_list_exact_words(keyword)
    with open(patients_file_path, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            row_pcm_id = row["pmcId"]
            row_article_date = row["articleDate"]
            row_comparison = word_tokenize(row["comparison"])
            comparison = row["comparison"]
            row_indication =  word_tokenize(row["indication"])
            indication = row["indication"]
            row_findings =  word_tokenize(row["findings"])
            findings = row["findings"]
            row_impression =  word_tokenize(row["impression"])
            impression = row["impression"]

            formatted_row = f"REPORT NO: {len(records) // 2 + 1}<br>"
            formatted_row += "____________________________________________<br>"
            formatted_row += f"pmcID: {pcm_id}<br>"
            formatted_row += f"ArticleDate: {article_date}<br>"
            formatted_row += f"Comparison: {comparison}<br>"
            formatted_row += f"Indication: {indication}<br>"
            formatted_row += f"Findings: {findings}<br>"
            formatted_row += f"Impression: {impression}<br>"
            formatted_row += "____________________________________________<br>"
            
            if (pcm_id and pcm_id == row_pcm_id):
                records.append(formatted_row)
                records.append("<br>")
            elif (article_date and article_date == row_article_date):   
                records.append(formatted_row)
                records.append("<br>")
            elif keyword:
                if SEARCH_MODE == 'some':
                    for key in keyword_list:
                        if (key in comparison or key in indication or key in findings or key in impression):   
                            report = str(row_findings) + " " + (str(row_impression))
                            if not is_negated(report.lower(), key.lower()): 
                                # Format the row with keywords in bold using HTML <b> tags
                                formatted_row = f"REPORT NO: {len(records) // 2 + 1}<br>"
                                formatted_row += "____________________________________________<br>"
                                formatted_row += f"pmcId: {row_pcm_id}<br>" 
                                formatted_row += f"articleDate: {row_article_date}<br>" 
                                if SEARCH_IN_COMPARISON:
                                    formatted_row += f"comparison: {highlight_keywords(row_comparison, key)}<br>" 
                                if SEARCH_IN_INDICATION:
                                    formatted_row += f"indication: {highlight_keywords(row_indication, key)}<br>" 
                                if SEARCH_IN_FINDINGS:
                                    formatted_row += f"findings: {highlight_keywords(row_findings, key)}<br>" 
                                if SEARCH_IN_IMPRESSION:
                                    formatted_row += f"impression: {highlight_keywords(row_impression, key)}<br>"
                                formatted_row += "____________________________________________<br><br>"

                                records.append(formatted_row)
                elif SEARCH_MODE == 'exact':
                    for key in keyword_list:
                        report = ""
                        if len(word_tokenize(key)) > 1:
                            if (key in comparison or key in indication or key in findings or key in impression):   
                                report = str(row_findings) + " " + (str(row_impression))
                        else:
                            if (key in row_comparison or key in row_indication or key in row_findings or key in row_impression):
                                report = str(row_findings) + " " + (str(row_impression))
                        
                        if report !="" and not is_negated(report.lower(), key.lower()): 
                            # Format the row with keywords in bold using HTML <b> tags
                            formatted_row = f"REPORT NO: {len(records) + 1}<br>"
                            formatted_row += "____________________________________________<br>"
                            formatted_row += f"pmcId: {row_pcm_id}<br>" 
                            formatted_row += f"articleDate: {row_article_date}<br>" 
                            if SEARCH_IN_COMPARISON:
                                formatted_row += f"comparison: {highlight_keywords(row_comparison, key)}<br>" 
                            if SEARCH_IN_INDICATION:
                                formatted_row += f"indication: {highlight_keywords(row_indication, key)}<br>" 
                            if SEARCH_IN_FINDINGS:
                                formatted_row += f"findings: {highlight_keywords(row_findings, key)}<br>" 
                            if SEARCH_IN_IMPRESSION:
                                formatted_row += f"impression: {highlight_keywords(row_impression, key)}<br>"
                            formatted_row += "____________________________________________<br><br>"

                            records.append(formatted_row)
    return remove_duplicates(records)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    load_radlex_mapping()
    global RESULTS     
    global SEARCH_MODE
    global SEARCH_IN_COMPARISON, SEARCH_IN_INDICATION, SEARCH_IN_FINDINGS, SEARCH_IN_IMPRESSION
    
    RESULTS = ["No records were found. Please try again with a different search criteria."]
    SEARCH_MODE = ""
    
    if request.method == 'POST':
        # Get the form data from the request
        pcmID = request.form['pcmID']
        articleDate = request.form['articleDate']
        keyword = request.form['keyword']

        # Get search mode: exact or some words
        search_mode = request.form.get('search_mode')
        if search_mode == 'exact':
            SEARCH_MODE = 'exact'
        elif search_mode == 'some':
            SEARCH_MODE = 'some'

        # Get the user's selections
        SEARCH_IN_COMPARISON = request.form.get('search_in_comparisons')
        SEARCH_IN_INDICATION = request.form.get('search_in_indications')
        SEARCH_IN_FINDINGS = request.form.get('search_in_findings')
        SEARCH_IN_IMPRESSION = request.form.get('search_in_impressions')

        # Perform the search and obtain results
        records = get_records(pcmID, articleDate, keyword)

        if records != []:
            RESULTS = records

        # Return the results as JSON
        return redirect(url_for("result"))
    

@app.route('/result')
def result():
    return render_template('result.html', results = RESULTS)


if __name__ == "__main__":
    app.run(port=8001, debug=True)
