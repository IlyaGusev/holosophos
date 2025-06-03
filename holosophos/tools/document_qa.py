from typing import Optional

from smolagents.tools import Tool  # type: ignore
from smolagents.models import Model  # type: ignore


SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions about documents accurately and concisely."
)
PROMPT = """Please answer the following questions based solely on the provided document.
If there is no answer in the document, output "There is no answer in the provided document".
First cite ALL relevant document fragments, then provide a final answer.
Answer all given questions one by one.
Make sure that you answer the actual questions, and not some other similar questions.

Questions:
{questions}

Document:
==== BEGIN DOCUMENT ====
{document}
==== END DOCUMENT ====

Questions (repeated):
{questions}

Your citations and answers:"""

DESCRIPTION = """
Answer questions about a document.
Use this tool when you need to find relevant information in a big document.
It takes questions and a document as inputs and generates an answer based on the document.

Example:
    >>> document = "The quick brown fox jumps over the lazy dog."
    >>> answer = document_qa(questions="What animal is mentioned? How many of them?", document=document)
    >>> print(answer)
    "The document mentions two animals: a fox and a dog. 2 animals."

Returns an answer to all questions based on the document content.
"""


class DocumentQATool(Tool):  # type: ignore
    name = "document_qa"
    description = DESCRIPTION
    inputs = {
        "questions": {
            "type": "string",
            "description": "Questions to be answered about the document.",
            "nullable": True,
        },
        "document": {
            "type": "string",
            "description": "The full text of the document to analyze.",
            "nullable": True,
        },
        "question": {
            "type": "string",
            "description": "Alias for 'questions'",
            "nullable": True,
        },
    }
    output_type = "string"

    def __init__(self, model: Model):
        self.model = model
        super().__init__()

    def forward(
        self,
        questions: Optional[str] = None,
        document: Optional[str] = None,
        question: Optional[str] = None,
    ) -> str:
        if question and not questions:
            questions = question
        assert questions and questions.strip(), "Please provide non-empty 'questions'"
        assert document and document.strip(), "Please provide non-empty 'document'"

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": PROMPT.format(questions=questions, document=document),
            },
        ]

        try:
            response = self.model(messages)
            if isinstance(response, str):
                return response.strip()
            final_response: str = response.content.strip()
            return final_response
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
