import pymupdf4llm

# Convert the PDF to Markdown
md_text = pymupdf4llm.to_text("data/resume.pdf")

print(md_text)