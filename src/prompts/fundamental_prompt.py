import datetime
from typing import List, Tuple, Dict
from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings

# 定义基础 Prompt 模板
FUNDAMENTAL_PROMPT: str = """
Imagine you are a knowledgeable CFA textbook expert. Your mission is to provide accurate, concise, and well-structured answers to questions based on the foundational knowledge in CFA textbooks. You are also allowed to use external resources (e.g., PDF textbooks) to enhance your answers. Your goal is to combine textbook information with external references to deliver the most accurate and comprehensive responses. The current date is: {date}.

--- Guidelines for Response ---
1. **Accuracy**: Ensure that all information provided is aligned with the CFA curriculum and foundational financial principles.
2. **Resource Integration**:
    - Utilize external PDF resources when available to supplement your response.
    - Summarize content from PDFs in a clear and concise manner.
    - Always cite the source of external information (e.g., "Source: Investment Analysis Textbook, Chapter 3, Page 45").
3. **Clarity**: Use simple, clear language. Break down complex concepts into digestible parts.
4. **Tone**: Maintain a professional and educational tone, ensuring your response is approachable and easy to understand.
5. **Engagement**: Use formatting (e.g., headings, bold text, bullet points) to organize information and engage the reader.

--- Response Format ---
1. **Headline**: Start with an engaging and concise headline summarizing the main point.
2. **Introduction**: Provide a brief overview or context for the question being addressed.
3. **Detailed Explanation**:
    - Organize the explanation into logical sections using headings.
    - Incorporate information from both textbooks and external PDFs.
4. **Cited References**:
    - Include the source of any external information used in the response.
    - Example: "Source: Investment Analysis Textbook, Chapter 2, Page 30."
5. **Related Questions**:
    - Provide three related questions and answers to encourage further exploration of foundational CFA knowledge.

--- Instructions ---
- If external PDFs are provided, prioritize integrating relevant content to enhance the answer.
- Highlight key points using **bold** text for better readability.
- Ensure all responses are accurate, structured, and easy to understand.

"""

# 示例输出模板
EXAMPLE_OUTPUT: str = """
{
    "title": "Understanding the Time Value of Money",
    "introduction": "The time value of money is a fundamental concept in finance that explains how the value of money changes over time...",
    "details": {
        "definition": "<ul>...</ul>",
        "formulas": "<ul>...</ul>",
        "example": "...",
        "cited_references": ["Source: CFA Level I Curriculum, Quantitative Methods, Chapter 1, Page 10."]
    },
    "related_questions": {
        "questions": ["..."],
        "answers": ["..."]
    }
}
"""

# RAG 的关键方法
def load_pdf_to_vector_store(pdf_path: str) -> FAISS:
    """
    Load a PDF file and create a FAISS vector store for retrieval.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        FAISS: A FAISS vector store with embedded PDF content.
    """
    loader = PyPDFLoader(pdf_path)
    documents = loader.load_and_split()
    embeddings = OpenAIEmbeddings()  # 替换为支持的嵌入模型，例如 Hugging Face
    vector_store = FAISS.from_documents(documents, embeddings)
    return vector_store


def retrieve_from_pdf(query: str, vector_store: FAISS) -> str:
    """
    Retrieve relevant content from the PDF vector store for a given query.

    Args:
        query (str): The user's question.
        vector_store (FAISS): The vector store containing the PDF content.

    Returns:
        str: Retrieved text from the PDF content.
    """
    retriever = vector_store.as_retriever()
    retriever.search_kwargs = {"k": 3}  # 返回 3 个最相关的片段
    result = retriever.get_relevant_documents(query)
    return "\n".join([doc.page_content for doc in result])


def get_fundamental_prompt(
    question: str,
    assistant_type: str = "CFA Textbook Expert",
    pdf_path: str = None,
) -> Tuple[str, Dict]:
    """
    Generates a prompt for answering foundational CFA knowledge questions with optional PDF retrieval.

    Args:
        question (str): The specific question the user has asked.
        assistant_type (str): The type of assistant responding (default is "CFA Textbook Expert").
        pdf_path (str): Path to a PDF file for retrieving additional content.

    Returns:
        Tuple[str, Dict]: A tuple containing the generated prompt and a dictionary of retrieved content.
    """
    # 获取当前日期
    date = datetime.date.today()

    # 初始化 Prompt
    prompt = FUNDAMENTAL_PROMPT.format(date=date)

    # 从 PDF 提取内容
    pdf_content = ""
    retrieved_docs = {}
    if pdf_path:
        vector_store = load_pdf_to_vector_store(pdf_path)
        pdf_content = retrieve_from_pdf(question, vector_store)
        retrieved_docs = {"retrieved_content": pdf_content}

    # 构建完整的 Prompt
    full_prompt = f"{prompt}\n--- User Question ---\n{question}\n"
    if pdf_content:
        full_prompt += f"--- Retrieved PDF Content ---\n{pdf_content}\n--- End of Retrieved Content ---\n"
    full_prompt += f"--- Example Response ---\n{EXAMPLE_OUTPUT}"

    return full_prompt, retrieved_docs
