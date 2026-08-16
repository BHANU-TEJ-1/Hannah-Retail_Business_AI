from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader


class DocumentLoader:
    """
    The loader takes the raw disk files and returnts the document objects required for the 
    vectorization in the next steps .Loads all Markdown documents from the documents folder.
    """

    def __init__(self):

        self.documents_path = Path("app/documents")

    def load_documents(self) -> list[Document]:

        documents = []

        markdown_files = sorted(
            self.documents_path.glob("*.md")
        )

        for file in markdown_files:

            loader = TextLoader(
                str(file),
                encoding="utf-8"
            )

            docs = loader.load()

            # Add useful metadata
            for doc in docs:

                doc.metadata["source"] = file.name
                doc.metadata["chapter"] = file.stem

            documents.extend(docs)

        return documents


document_loader = DocumentLoader()