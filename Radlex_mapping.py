import csv

radlex_file_path = "updated_RADLEX.csv"

file_path = "radlex_mapping.csv"

def load_radlex_mapping(radlex_file_path):
    radlex_mapping = {}

    # Load RadLex mapping from CSV
    with open(radlex_file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for item in reader:
            preferred_label = item['Preferred.Label']
            synonyms = item['Synonyms']
            radlex_mapping[preferred_label] = synonyms

    return radlex_mapping

def write_radlex_mapping_to_csv(radlex_mapping, output_file_path):
    # Write the dictionary to a CSV file
    with open(output_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['RadLex Term', 'Synonym']
        writer = csv.writer(csvfile)
        writer.writerow(fieldnames)

        for preferred_label, synonyms in radlex_mapping.items():
            writer.writerow([preferred_label, synonyms])


if __name__ == "__main__":
    radlex_mapping = load_radlex_mapping(radlex_file_path)
    # Write the RadLex mapping to a new CSV file
    write_radlex_mapping_to_csv(radlex_mapping, file_path)