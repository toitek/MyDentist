import os
import shutil
import csv
import pickle

from langchain.document_loaders.csv_loader import CSVLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS


def split_csv(file_path, max_rows=100, output_dir="./csv"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        header = next(csvreader)
        file_number = 1
        rows = []

        for row in csvreader:
            rows.append(row)
            if len(rows) == max_rows:
                output_file_path = os.path.join(output_dir, f"split_{file_number}.csv")
                with open(output_file_path, 'w', newline='') as output_file:
                    csvwriter = csv.writer(output_file)
                    csvwriter.writerow(header)
                    csvwriter.writerows(rows)
                file_number += 1
                rows = []

        if rows:
            output_file_path = os.path.join(output_dir, f"split_{file_number}.csv")
            with open(output_file_path, 'w', newline='') as output_file:
                csvwriter = csv.writer(output_file)
                csvwriter.writerow(header)
                csvwriter.writerows(rows)



def process_and_delete_csv(file_path, vectorstore):
    loader = CSVLoader(file_path=file_path, csv_args={
        'delimiter': ',',
        'fieldnames': ['question', 'answer']
    })
    data = loader.load()

    embeddings = OpenAIEmbeddings()
    vectorstore =  FAISS.from_documents(data, embeddings)

    os.remove(file_path)


def ingest_docs():
    split_csv("./dentist.csv")

    vectorstore = None

    csv_folder = "./csv"
    for file_name in os.listdir(csv_folder):
        file_path = os.path.join(csv_folder, file_name)

        loader = CSVLoader(file_path=file_path, csv_args={
            'delimiter': ',',
            'fieldnames': ['question', 'answer']
        })
        data = loader.load()

        embeddings = OpenAIEmbeddings()
        if vectorstore is None:
            vectorstore = FAISS.from_documents(data, embeddings)
        else:
            new_vectorstore = FAISS.from_documents(data, embeddings)
            vectorstore.merge_from(new_vectorstore)

        os.remove(file_path)

    with open("vectorstore.pkl", "wb") as f:
        pickle.dump(vectorstore, f)

if __name__ == "__main__":
    ingest_docs()



