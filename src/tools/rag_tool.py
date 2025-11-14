from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.tools import BaseTool
import os
import yaml
from langchain.schema import Document

from paths import DATA_PATH

THRESHOLD = 1.25
TOP_K = 5


class RAGTool(BaseTool):
    name: str = "RAGTool"
    description: str = (
        "Retrieve the most relevant sections from the dataset (DataFrame) documentation using Retrieval-Augmented Generation (RAG). "
        "Use this tool to locate attributes, fields, or columns that may be relevant to a query about the data. "
        "Each section in the documentation includes a column name, description, and data type. "
        "Given a natural language query, the tool returns the top-k most relevant columns with descriptions. "
        "\n\n"
        "👉 To get the best results, structure your query in the following format:\n"
        "    'What attributes are related to [concept or goal] where [optional condition]?' \n"
        "Examples:\n"
        "- 'What attributes are related to product type and quantity where we want the top 5 transported items?'\n"
        "- 'What attributes are related to vendor contact where the order is pending?'\n"
        "- 'What attributes are related to transport location or delivery address?'\n"
        "\n"
        "This helps the tool better retrieve relevant columns based on the structured documentation."
    )
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    vectorstore: FAISS = None
    data_embeddings: HuggingFaceEmbeddings = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_embeddings = HuggingFaceEmbeddings(model_name=self.model_name)

        # Load YAML file
        yaml_file_path = os.path.join(DATA_PATH, "..", "data_documentation.yaml")
        with open(yaml_file_path) as f:
            data = yaml.safe_load(f)

        # Create LangChain documents from YAML
        docs = []
        for column in data["columns"]:
            # Create metadata with all column attributes
            metadata = {"name": column, "data_type":data['columns'][column]["data_type"]}

            # Include both name and description in the content for better search
            description = data['columns'][column].get("description", "")
            data_type = data['columns'][column].get("data_type", "")
            additional_notes = data['columns'][column].get("additional_notes", "")
            content = (
                f"Column: {column}\n"
                f"Description: {description}\n"
                f"Data Type: {data_type}"
            )
            if additional_notes:
                content += f"\nAdditional notes: {additional_notes}"

            doc = Document(page_content=content, metadata=metadata)
            docs.append(doc)

        self.vectorstore = FAISS.from_documents(docs, self.data_embeddings)

    def _run(self, query_text: str):
        if not self.vectorstore:
            raise ValueError("Vectorstore is not created. Please load documents first.")

        # Get documents with their similarity scores
        results = self.vectorstore.similarity_search_with_score(query_text, k=TOP_K)

        # Format results with more information
        formatted_results = []
        for doc, score in results:
            # if score <= THRESHOLD:
                result_entry = {
                    "column": doc.metadata["name"],
                    "description": doc.page_content.split("\nDescription: ")[1].split(
                        "\n"
                    )[0],
                    "data_type": doc.metadata["data_type"],
                    "score": float(score),
                }
                formatted_results.append(result_entry)

        return (
            formatted_results
            if formatted_results
            else "No relevant columns found matching your query."
        )
