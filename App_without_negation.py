'''
This is the main file for the application. It contains the routes and the logic for the application. It consists of basic search without any 
negation or RadLex ontology.
'''

from flask import Flask, redirect, url_for, render_template, request
import csv
import nltk
from nltk.tokenize import word_tokenize
import re

app = Flask(__name__)

# File paths
patients_file_path = "updated_patient_records.csv"
radlex_file_path = "updated_RADLEX.csv"

RESULTS = ["No records were found. Please try again with a different search criteria."]
SEARCH_MODE = ""
SEARCH_IN_COMPARISON = True
SEARCH_IN_INDICATION = True
SEARCH_IN_FINDINGS = True
SEARCH_IN_IMPRESSION = True


# Remove duplicate records in the output file
def remove_duplicates(raw_records):
    unique_data = []
    for record in raw_records:
        if record not in unique_data:
            unique_data.append(record)
    return unique_data


def highlight_keywords(text_str, keyword):
    # Use regular expression to replace the keywords with <b> tags around them
    # highlighted_text = re.sub(r'\b' + re.escape(keyword) + r'\S' +  r'\b', f'<b>{keyword}</b>', text_str, flags=re.IGNORECASE)
    highlighted_text = re.sub(r'\b' + re.escape(keyword), f'<b>{keyword}</b>', text_str, flags=re.IGNORECASE)
    return highlighted_text


# Get records based on search criteria
def get_records(pcm_id, article_date, keyword):
    records = []
    global SEARCH_MODE

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

            formatted_row = f"REPORT NO: {len(records) + 1}<br>"
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
                    keyword_list = nltk.word_tokenize(keyword)

                    for key in keyword_list:
                    #print("key: ", key)
                        if (key in row_comparison or key in row_indication or key in row_findings or key in row_impression):   
                            # Format the row with keywords in bold using HTML <b> tags
                            formatted_row = f"REPORT NO: {len(records) + 1}<br>"
                            formatted_row += "____________________________________________<br>"
                            formatted_row += f"pmcId: {row_pcm_id}<br>" 
                            formatted_row += f"articleDate: {row_article_date}<br>" 
                            if SEARCH_IN_COMPARISON:
                                formatted_row += f"comparison: {highlight_keywords(comparison, key)}<br>" 
                            if SEARCH_IN_INDICATION:
                                formatted_row += f"indication: {highlight_keywords(indication, key)}<br>" 
                            if SEARCH_IN_FINDINGS:
                                formatted_row += f"findings: {highlight_keywords(findings, key)}<br>" 
                            if SEARCH_IN_IMPRESSION:
                                formatted_row += f"impression: {highlight_keywords(impression, key)}<br>"
                            formatted_row += "____________________________________________<br><br>"

                            records.append(formatted_row)

                elif SEARCH_MODE == 'exact':
                    key = keyword.lower()
                    if len(word_tokenize(key)) > 1:
                        if (key in comparison or key in indication or key in findings or key in impression):   
                            # Format the row with keywords in bold using HTML <b> tags
                            formatted_row = f"REPORT NO: {len(records) + 1}<br>"
                            formatted_row += "____________________________________________<br>"
                            formatted_row += f"pmcId: {row_pcm_id}<br>" 
                            formatted_row += f"articleDate: {row_article_date}<br>" 
                            if SEARCH_IN_COMPARISON:
                                formatted_row += f"comparison: {highlight_keywords(comparison, key)}<br>" 
                            if SEARCH_IN_INDICATION:
                                formatted_row += f"indication: {highlight_keywords(indication, key)}<br>" 
                            if SEARCH_IN_FINDINGS:
                                formatted_row += f"findings: {highlight_keywords(findings, key)}<br>" 
                            if SEARCH_IN_IMPRESSION:
                                formatted_row += f"impression: {highlight_keywords(impression, key)}<br>"
                            formatted_row += "____________________________________________<br><br>"

                            records.append(formatted_row)
                    else:
                        if (key in row_comparison or key in row_indication or key in row_findings or key in row_impression):                     
                            # Format the row with keywords in bold using HTML <b> tags
                            formatted_row = f"REPORT NO: {len(records) + 1}<br>"
                            formatted_row += "____________________________________________<br>"
                            formatted_row += f"pmcId: {row_pcm_id}<br>" 
                            formatted_row += f"articleDate: {row_article_date}<br>" 
                            if SEARCH_IN_COMPARISON:
                                formatted_row += f"comparison: {highlight_keywords(comparison, key)}<br>" 
                            if SEARCH_IN_INDICATION:
                                formatted_row += f"indication: {highlight_keywords(indication, key)}<br>" 
                            if SEARCH_IN_FINDINGS:
                                formatted_row += f"findings: {highlight_keywords(findings, key)}<br>" 
                            if SEARCH_IN_IMPRESSION:
                                formatted_row += f"impression: {highlight_keywords(impression, key)}<br>"
                            formatted_row += "____________________________________________<br><br>"

                            records.append(formatted_row)      

    return remove_duplicates(records)
    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
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
    app.run(port=8000, debug=True)
