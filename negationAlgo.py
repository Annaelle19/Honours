import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
import re
import pandas as pd
import csv


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

    # Negation cues
    negation_cues = ["no", "denies", "denied", "without", "not", "no evidence", "with no", "negative for", "rule out", "ruled out",
                     "no significant", "no new", "no abnormal", "no suspicious", "absence of", "no signs of", "no sign of",
                       "no symptoms of", "no cause of", "without indication of", "negative", "clear", "clear of"]

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
                if token in negation_cues:
                    is_negated = True
                    break


    if UML_present and not is_negated:
        return True
    else:
        return False



patients_file_path = "updated_patient_records.csv"
UML = input("Enter the term you want to search: ")  # Term we want to find

with open(patients_file_path, "r") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        id = row["pmcId"]
        indication_column = row["indication"]
        findings_column = row["findings"]
        impression_column = row["impression"]

        # Combine indication, findings and impression into a single report
        report = str(findings_column) + " " + (str(impression_column))

        if is_negated((report).lower(), UML.lower()):
            print("pmcID: " + str(id) + ", report: " + report + "\n")



