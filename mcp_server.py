from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
from pydantic import Field

# Python MCP SDK - very easy to build; no need to build tool schema manually.
mcp = FastMCP("DocumentMCP", log_level="ERROR")

# Docs exist in memory (mock docs)
docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}


# Tool - Read Doc (take name and return content)
@mcp.tool(
    name="read_doc_contents",
    description="This tool reads the contents of the document and returns in a string",
)
def read_document(
        doc_id: str = Field(description="The ID of the document to read.")
) -> str:
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found.")
    return docs[doc_id]


# Tool - Update Doc
@mcp.tool(
    name="edit_document",
    description="This tool edits a document by replacing a string in the document's content with a new string.",
)
def edit_document(
        doc_id: str = Field(description="The ID of the document to update."),
        old_string: str = Field(description="The old string to edit. Must match exactly, including whitespaces."),
        new_string: str = Field(description="The new string to edit.")
):
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found.")
    docs[doc_id] = docs[doc_id].replace(old_string, new_string)


# Resource - return all doc id's (@)
@mcp.resource(
    "docs://documents",  # URI
    mime_type='application/json'  # SDK Will turn into string
)
def list_docs() -> list[str]:
    # Returns list of document names - then this will show in cli (through CLI class)
    return list(docs.keys())


# Resource - return contents of specific @document
@mcp.resource(
    "docs://documents/{doc_id}",  # URI
    mime_type='text/plain'
)
def fetch_doc(doc_id: str) -> str:
    # Returns content - then this will show in cli (through CLI class)
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found.")
    return docs[doc_id]


@mcp.prompt(
    name="format",
    description="This tool rewrites the document in Markdown format",
)
def format_document(
        doc_id: str = Field(description="Id of the document to format")  # Must be provided by Client call
) -> list[base.Message]:
    prompt = f"""
    Your goal is to reformat a document to be written with markdown syntax.

    The id of the document you need to reformat is:
    <document_id>
    {doc_id}
    </document_id>

    Add in headers, bullet points, tables, etc as necessary. Feel free to add in extra text, but don't change the meaning of the report.
    Use the 'edit_document' tool to edit the document. After the document has been edited, respond with the final version of the doc. Don't explain your changes.
    """
    return [base.UserMessage(prompt)]


@mcp.prompt(
    name="summarise",
    description="This tool summarises the contents of the document",
)
def summarise_document(doc_id: str) -> list[base.Message]:
    prompt = f"""

    Your goal is to summarise the contents of the document:
    
    The id of the document you need to summarise is:
    <document_id>
    {doc_id}
    </document_id>
    
    """
    return [base.UserMessage(prompt)]


if __name__ == "__main__":
    mcp.run(transport="stdio")
