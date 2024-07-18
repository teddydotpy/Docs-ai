import argparse
import csv
from ast_handler import DocumentationHandler, DocumentGenerator

def process_directory(directory_path):
    print(f"Processing files in directory: {directory_path}")
    docs = DocumentationHandler().document_code_base(dir_path=directory_path)
    DocumentGenerator().create_document(docs=docs)


def process_file_list(file_list):
    print(f"Processing files in the list: {file_list}")
    docs = DocumentationHandler().document_file_list(list_of_paths=file_list)
    DocumentGenerator().create_document(docs=docs)

def process_single_file(file_path):
    print(f"Processing a single file: {file_path}")
    docs = DocumentationHandler().document_file(file_path=file_path)
    DocumentGenerator().create_document(docs=docs)

def main():
    parser = argparse.ArgumentParser(description="Script to process files based on input arguments.")
    parser.add_argument("-d", "--directory", help="Path to the directory containing files.")
    parser.add_argument("-fl", "--file_list", help="CSV file or comma-separated list of files.")
    parser.add_argument("-l", "--single_file", help="Path to a single file.")
    
    args = parser.parse_args()

    if not any([args.directory, args.file_list, args.single_file]):
        parser.error("Please provide one of the following options: -d (directory), -fl (file_list), -l (single_file).")

    if args.directory:
        process_directory(args.directory)
    elif args.file_list:
        if args.file_list.endswith('.csv'):
            with open(args.file_list, 'r') as csv_file:
                file_list = [row[0] for row in csv.reader(csv_file)]
        else:
            file_list = args.file_list.split(',')
        process_file_list(file_list)
    elif args.single_file:
        process_single_file(args.single_file)

if __name__ == "__main__":
    main()
