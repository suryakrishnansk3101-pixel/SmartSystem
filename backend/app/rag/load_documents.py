from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader
)
from langchain_core.documents import Document

import os
import pandas as pd


def _clean_value(value):

    if pd.isna(value):
        return ""

    return str(value).strip()


def _load_table_rows(file_path):

    if file_path.lower().endswith(".csv"):
        sheets = {"Sheet1": pd.read_csv(file_path)}
    else:
        sheets = pd.read_excel(file_path, sheet_name=None)

    documents = []

    for sheet_name, dataframe in sheets.items():

        columns = {
            str(column).strip().lower(): column
            for column in dataframe.columns
        }

        question_column = (
            columns.get("question")
            or columns.get("questions")
            or columns.get("faq")
        )

        answer_column = (
            columns.get("answer")
            or columns.get("answers")
            or columns.get("solution")
            or columns.get("response")
        )

        for row_number, row in dataframe.iterrows():

            if question_column and answer_column:

                question = _clean_value(row.get(question_column))
                answer = _clean_value(row.get(answer_column))

                if not question and not answer:
                    continue

                content = (
                    f"FAQ Question: {question}\n"
                    f"FAQ Answer: {answer}"
                )

            else:

                values = [
                    f"{column}: {_clean_value(row.get(column))}"
                    for column in dataframe.columns
                    if _clean_value(row.get(column))
                ]

                if not values:
                    continue

                content = "\n".join(values)

            documents.append(
                Document(
                    page_content=content,
                    metadata={
                        "source": file_path,
                        "source_type": "faq_file",
                        "sheet": sheet_name,
                        "row": int(row_number) + 2
                    }
                )
            )

    return documents


def load_documents():

    all_docs = []

    upload_folder = "data/uploads"

    if not os.path.exists(upload_folder):
        print("Upload folder not found")
        return all_docs

    print("Scanning:", upload_folder)

    for file in os.listdir(upload_folder):

        file_path = os.path.join(
            upload_folder,
            file
        )

        print("Loading:", file_path)

        try:

            if file.lower().endswith(".pdf"):

                loader = PyPDFLoader(
                    file_path
                )

                all_docs.extend(
                    loader.load()
                )

            elif file.lower().endswith(
                (".docx", ".doc")
            ):

                loader = Docx2txtLoader(
                    file_path
                )

                all_docs.extend(
                    loader.load()
                )

            elif file.lower().endswith(
                (".xlsx", ".xls")
            ):

                all_docs.extend(
                    _load_table_rows(file_path)
                )

            elif file.lower().endswith(".csv"):

                all_docs.extend(
                    _load_table_rows(file_path)
                )

            else:

                print(
                    f"Skipped unsupported file: {file}"
                )

        except Exception as e:

            print(
                f"Error loading {file}: {e}"
            )

    print(
        "Total documents:",
        len(all_docs)
    )

    return all_docs
