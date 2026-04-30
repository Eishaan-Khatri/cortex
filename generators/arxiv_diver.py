"""
CORTEX — ArXiv PDF Deep-Diver
Downloads, parses, and summarizes the latest academic papers.
"""

import os
import arxiv
import fitz  # PyMuPDF
from core.utils import extract_keywords_from_text

def fetch_top_paper(topic):
    """Fetch the top recent paper from ArXiv related to the topic."""
    # Build a search query based on the topic and its subtopics
    query = f'"{topic["full_name"]}"'
    if topic.get("subtopics"):
        sub_query = " OR ".join([f'"{st}"' for st in topic["subtopics"][:3]])
        query = f'({query}) AND ({sub_query})'
    
    print(f"  [ARXIV] Searching: {query[:50]}...")
    
    client = arxiv.Client()
    search = arxiv.Search(
        query=query,
        max_results=5,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    try:
        results = list(client.results(search))
        if not results:
            return None
        # Return the most recent one
        return results[0]
    except Exception as e:
        print(f"  [ARXIV] Search failed: {e}")
        return None

def extract_text_from_pdf(pdf_path, max_pages=5):
    """Extract text from the first few pages of a PDF."""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        # We only need the first few pages (abstract, intro, methodology) to get the core idea
        num_pages = min(len(doc), max_pages)
        for i in range(num_pages):
            page = doc.load_page(i)
            text += page.get_text()
        return text
    except Exception as e:
        print(f"  [ARXIV] PDF parsing failed: {e}")
        return ""

def deep_dive_paper(ai, topic, persona_prompt):
    """Fetch, read, and summarize an ArXiv paper."""
    paper = fetch_top_paper(topic)
    if not paper:
        return None

    print(f"  [ARXIV] Selected: {paper.title[:60]}...")
    
    # Download the PDF temporarily
    pdf_filename = f"temp_{paper.get_short_id()}.pdf"
    try:
        paper.download_pdf(filename=pdf_filename)
        print(f"  [ARXIV] Downloaded PDF. Parsing...")
        paper_text = extract_text_from_pdf(pdf_filename)
        os.remove(pdf_filename) # Cleanup
    except Exception as e:
        print(f"  [ARXIV] Failed to download or parse PDF: {e}")
        if os.path.exists(pdf_filename):
            os.remove(pdf_filename)
        return None

    if not paper_text:
        return None

    print("  [ARXIV] Analyzing paper content...")
    
    prompt = f"""
    {persona_prompt}
    
    I have extracted the text from a recent academic paper titled "{paper.title}" by {paper.authors[0].name} et al.
    
    Here is the raw text from the first few pages:
    ---
    {paper_text[:8000]} # Limit to ~8000 chars to save context window
    ---
    
    Perform a highly technical "Deep Dive" into this paper. 
    Write a 1-page markdown document that includes:
    1. A tl;dr summary.
    2. The core methodology or architecture proposed.
    3. The key results or findings.
    4. CORTEX's critical analysis of its limitations or potential impact on the field.
    
    Format it beautifully using Markdown headers, bullet points, and blockquotes where appropriate.
    Do not wrap the entire response in a markdown block, just return the raw markdown.
    """
    
    summary = ai.generate(prompt)
    if not summary:
        return None

    # Format the final document
    doc_content = f"# Deep Dive: {paper.title}\n\n"
    doc_content += f"**Authors:** {', '.join([a.name for a in paper.authors])}\n"
    doc_content += f"**Published:** {paper.published.strftime('%Y-%m-%d')}\n"
    doc_content += f"**ArXiv ID:** [{paper.get_short_id()}]({paper.entry_id})\n\n"
    doc_content += "---\n\n"
    doc_content += summary

    # Clean filename
    safe_title = "".join([c if c.isalnum() else "_" for c in paper.title]).strip("_")
    safe_title = safe_title[:50]
    date_str = paper.published.strftime('%Y%m%d')
    filename = f"papers/{date_str}_{safe_title}.md"
    
    return {
        "filename": filename,
        "content": doc_content,
        "title": paper.title,
        "keywords": extract_keywords_from_text(summary)
    }
