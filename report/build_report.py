"""Build the final Mini Project Report for the Multilingual Document
Summarizer, following the AISSMS format closely (Times New Roman, Heading
1-4 styles, Table Grid, tab-based table of contents)."""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
SCREENSHOT = ROOT / "docs" / "screenshot.png"
OUT = ROOT / "report" / "Mini_Project_Report_Multilingual_Summarizer.docx"

FONT = "Times New Roman"

ALIGN = {
    "left": WD_ALIGN_PARAGRAPH.LEFT,
    "center": WD_ALIGN_PARAGRAPH.CENTER,
    "right": WD_ALIGN_PARAGRAPH.RIGHT,
    "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
}


def base_document() -> Document:
    doc = Document()
    sec = doc.sections[0]
    sec.page_height = Cm(29.7)
    sec.page_width = Cm(21.0)
    sec.top_margin = Cm(2.2)
    sec.bottom_margin = Cm(2.0)
    sec.left_margin = Cm(2.2)
    sec.right_margin = Cm(1.8)

    for name in ("Normal", "Heading 1", "Heading 2", "Heading 3", "Heading 4", "Body Text", "List Paragraph"):
        try:
            style = doc.styles[name]
        except KeyError:
            continue
        style.font.name = FONT
        try:
            style.font.color.rgb = RGBColor(0, 0, 0)
        except Exception:
            pass
    doc.styles["Normal"].font.size = Pt(12)

    fp = sec.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = fp.add_run()
    for tag, attr, text in (
        ("w:fldChar", "begin", None),
        ("w:instrText", None, "PAGE"),
        ("w:fldChar", "end", None),
    ):
        el = OxmlElement(tag)
        if attr:
            el.set(qn("w:fldCharType"), attr)
        if text:
            el.set(qn("xml:space"), "preserve")
            el.text = text
        run._r.append(el)
    return doc


def para(doc, text="", style="Normal", size=12, bold=False, italic=False,
         align="left", before=0, after=6):
    p = doc.add_paragraph(style=style)
    p.alignment = ALIGN[align]
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    if text:
        r = p.add_run(text)
        r.bold = bold
        r.italic = italic
        r.font.size = Pt(size)
        r.font.name = FONT
    return p


def heading(doc, text, level, align="center"):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.alignment = ALIGN[align]
    p.add_run(text)
    return p


def toc_line(doc, text, page):
    p = doc.add_paragraph(style="Normal")
    p.paragraph_format.tab_stops.add_tab_stop(Cm(16.5), WD_TAB_ALIGNMENT.RIGHT)
    r = p.add_run(f"{text}\t{page}")
    r.font.size = Pt(11)
    r.font.name = FONT
    return p


def chapter(doc, number, title):
    doc.add_page_break()
    para(doc, f"CHAPTER {number}", size=16, bold=True, align="center", after=2)
    para(doc, title.upper(), size=16, bold=True, align="center", after=12)


def section(doc, number, title):
    para(doc, f"{number} {title}", style="Body Text", size=12, bold=True,
         align="left", before=10, after=4)


def subsection(doc, text):
    para(doc, text, style="Body Text", size=12, bold=True, align="left", before=6, after=2)


def table(doc, headers, rows, widths=None, caption=None):
    if caption:
        para(doc, caption, style="Body Text", size=10, bold=True, before=8, after=4)
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, htext in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = ""
        r = cell.paragraphs[0].add_run(htext)
        r.bold = True
        r.font.size = Pt(10)
        r.font.name = FONT
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(val))
            r.font.size = Pt(10)
            r.font.name = FONT
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    para(doc, "", after=2)
    return t


def bullets(doc, items):
    for it in items:
        p = doc.add_paragraph(style="List Paragraph")
        p.paragraph_format.left_indent = Cm(0.8)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(f"• {it}")
        r.font.size = Pt(12)
        r.font.name = FONT


def numbered(doc, items, start=1):
    for i, it in enumerate(items, start):
        p = doc.add_paragraph(style="List Paragraph")
        p.paragraph_format.left_indent = Cm(0.8)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(f"{i}. {it}")
        r.font.size = Pt(12)
        r.font.name = FONT


doc = base_document()

# ---------------------------------------------------------------- TITLE PAGE
para(doc, "", after=6)
heading(doc, "A Mini Project Report", 4)
para(doc, "on", align="center", after=4)
heading(doc, "Multilingual Document Summarizer", 2)
heading(doc, "Submitted to", 2)
heading(doc, "AISSMS College of Engineering, Pune", 2)
para(doc, "In partial fulfillment of the requirements for the Third Year of the Degree of",
     align="center", after=2)
heading(doc, "BE/BTech", 3)
para(doc, "in", align="center", after=2)
heading(doc, "Artificial Intelligence and Machine Learning", 2)
para(doc, "Submitted by", align="center", after=2)
para(doc, "1. Hardik Pathak – ______________", style="List Paragraph", align="center", after=2)
para(doc, "2. ______________________________", style="List Paragraph", align="center", after=2)
para(doc, "3. ______________________________", style="List Paragraph", align="center", after=10)
para(doc, "Under the guidance of", align="center", after=2)
heading(doc, "Prof. ______________________", 3)
para(doc, "Department of Artificial Intelligence and Machine Learning", align="center", after=2)
heading(doc, "AISSMS College of Engineering", 1)
para(doc, "Kennedy Road, Pune – 411001, Maharashtra, India", align="center", after=12)
heading(doc, "Academic Year: 2026–2027", 3)

# ---------------------------------------------------------------- CERTIFICATE
doc.add_page_break()
para(doc, "CERTIFICATE", size=14, bold=True, align="center", after=14)
para(doc, "This is to certify that the project report entitled \u201cMultilingual Document "
     "Summarizer\u201d is a record of bonafide work carried out by the students under the "
     "supervision and guidance of Prof. ____________________, in partial fulfillment of the "
     "requirements for the Third Year (Artificial Intelligence and Machine Learning) programme "
     "of AISSMS College of Engineering, Pune, during the academic year 2026–2027.",
     style="Body Text", size=12, align="justify", after=16)
para(doc, "Date:", size=12, after=2)
para(doc, "Place: Pune", size=12, after=24)
para(doc, "Submitted by:", size=12, bold=True, after=2)
para(doc, "1. Hardik Pathak – ______________", style="List Paragraph", after=2)
para(doc, "2. ______________________________", style="List Paragraph", after=2)
para(doc, "3. ______________________________", style="List Paragraph", after=24)
para(doc, "____________________\t\t\t____________________", size=12, after=0)
para(doc, "Prof. ________________    \t\t\tDr. ________________", size=11, after=0)
para(doc, "Project Guide\t\t\t\tHead of Department", size=11)

# ---------------------------------------------------------------- ACKNOWLEDGEMENT
doc.add_page_break()
para(doc, "ACKNOWLEDGEMENT", size=14, bold=True, align="center", after=14)
para(doc, "We would like to express our sincere gratitude to our project guide for providing "
     "valuable guidance, encouragement, and support throughout the development of our mini "
     "project, \u201cMultilingual Document Summarizer\u201d. Their valuable suggestions, "
     "constructive feedback, and continuous motivation helped us understand the project "
     "requirements and complete the work successfully.", style="Body Text", align="justify")
para(doc, "We are thankful to our Head of Department and all faculty members for giving us the "
     "opportunity to work on this project as part of our Natural Language Processing (NLP) "
     "curriculum. Their guidance and support encouraged us to explore the practical applications "
     "of Natural Language Processing.", style="Body Text", align="justify")
para(doc, "We would also like to extend our sincere thanks to our college for providing the "
     "necessary facilities, resources, and a positive learning environment throughout the project "
     "development process.", style="Body Text", align="justify")
para(doc, "Through this project, we gained practical experience in text preprocessing, abstractive "
     "summarization using Transformer-based models (BART and IndicBART), Optical Character "
     "Recognition, model fine-tuning on Kaggle GPUs, ROUGE-based evaluation, and web application "
     "development using Python, FastAPI, and Streamlit.", style="Body Text", align="justify")
para(doc, "We would also like to acknowledge the open-source datasets and models (CNN/DailyMail, "
     "XL-Sum, Hugging Face Transformers, EasyOCR) that helped us understand the tools used in "
     "this project.", style="Body Text", align="justify")
para(doc, "Finally, we are thankful to everyone who directly or indirectly supported us during the "
     "completion of this mini project. We hope that the system can contribute towards easier "
     "access to long documents for readers of English and Hindi.", style="Body Text", align="justify")

# ---------------------------------------------------------------- ABSTRACT
doc.add_page_break()
para(doc, "ABSTRACT", size=14, bold=True, align="center", after=14)
para(doc, "Multilingual Document Summarizer is a web-based application that produces concise, "
     "abstractive summaries of long documents and images in English and Hindi. Large amounts of "
     "useful information are locked inside PDF files, Word documents, plain-text files, and "
     "scanned images, and readers often need to spend considerable time locating the key points. "
     "Language is an additional barrier, because most existing summarization tools support "
     "English only.", style="Body Text", align="justify")
para(doc, "The system accepts .txt, .pdf, and .docx files, images (.png, .jpg), and pasted text. "
     "Document text is extracted using PyMuPDF and python-docx, and image text is extracted using "
     "OCR (EasyOCR locally, or Gemini vision in the cloud). The extracted text is passed to a "
     "language-specific sequence-to-sequence model that generates an abstractive summary. English "
     "documents are summarized using BART fine-tuned on CNN/DailyMail, and Hindi documents using "
     "IndicBART fine-tuned on XL-Sum.", style="Body Text", align="justify")
para(doc, "The application is developed using Python and the Hugging Face Transformers library. "
     "The user interface is provided as a FastAPI-backed web application with an "
     "HTML/CSS/JavaScript frontend and as a Streamlit demo. The models were fine-tuned on an "
     "NVIDIA T4 GPU and evaluated using ROUGE. An optional Gemini API backend allows the app to "
     "run without downloading local models.", style="Body Text", align="justify")
para(doc, "The main objective of the project is to make long documents easier to understand and "
     "to make summarization available to readers of Hindi as well as English.",
     style="Body Text", align="justify")
para(doc, "Keywords: Natural Language Processing (NLP), Abstractive Summarization, Tokenization, "
     "BART, IndicBART, XL-Sum, Optical Character Recognition (OCR), Multilingual, Fine-tuning, "
     "ROUGE, FastAPI, Streamlit, Gemini API.", style="Body Text", size=11, italic=True, align="justify")

# ---------------------------------------------------------------- CONTENT
doc.add_page_break()
para(doc, "CONTENT", size=14, bold=True, align="center", after=10)
para(doc, "Chapter / Contents", bold=True, after=2)
toc = [
    ("Acknowledgement", "i"), ("Abstract", "ii"), ("Table of Contents", "iii"),
    ("List of Figures", "iv"), ("List of Tables", "v"),
    ("Chapter 1: Introduction", "1"),
    ("1.1 Introduction to the Project", "1"), ("1.2 Background and Motivation", "1"),
    ("1.3 Problem Statement", "2"), ("1.4 Objectives", "2"),
    ("1.5 Scope of the Project", "2"), ("1.6 Applications of the Project", "3"),
    ("Chapter 2: Literature Review", "4"),
    ("2.1 Review of Existing Research Papers", "4"), ("2.2 Existing System", "5"),
    ("2.3 Limitations of Existing System", "5"), ("2.4 Research Gap", "5"),
    ("Chapter 3: Problem Statement and Requirements", "6"),
    ("3.1 Problem Definition", "6"), ("3.2 Proposed Solution", "6"),
    ("3.3 Functional Requirements", "6"), ("3.4 Non-Functional Requirements", "7"),
    ("3.5 Hardware and Software Requirements", "7"),
    ("Chapter 4: Proposed Methodology", "8"),
    ("4.1 Overview of the Proposed System", "8"), ("4.2 System Architecture", "8"),
    ("4.3 Workflow of the System", "9"), ("4.4 NLP Techniques and Algorithms", "9"),
    ("4.5 Dataset Collection and Preprocessing", "11"),
    ("Chapter 5: System Design and Implementation", "12"),
    ("5.1 System Design", "12"), ("5.2 Flowchart / UML / DFD Diagrams", "12"),
    ("5.3 Tools, Technologies and Libraries", "13"), ("5.4 Implementation Details", "13"),
    ("5.5 User Interface and Screenshots", "14"),
    ("Chapter 6: Results and Discussion", "15"),
    ("6.1 Experimental Setup", "15"), ("6.2 Test Cases and Sample Outputs", "15"),
    ("6.3 Performance Evaluation Metrics", "16"), ("6.4 Results and Observations", "16"),
    ("6.5 Limitations", "17"),
    ("Chapter 7: Conclusion and Future Scope", "18"),
    ("7.1 Conclusion", "18"), ("7.2 Future Scope", "18"),
    ("References", "19"),
    ("Appendix A: Important Code Snippets", "20"),
    ("Appendix B: Additional Screenshots / Outputs", "21"),
]
for text, page in toc:
    toc_line(doc, text, page)

# ---------------------------------------------------------------- LIST OF FIGURES
doc.add_page_break()
para(doc, "LIST OF FIGURES", size=14, bold=True, align="center", after=10)
table(doc, ["Figure Title", "Page No."], [
    ["Fig. 1.1: Overview of the Summarization Pipeline", "3"],
    ["Fig. 2.1: Existing Summarization Workflow", "6"],
    ["Fig. 4.1: Proposed System Architecture", "8"],
    ["Fig. 4.2: Workflow of the Proposed System", "9"],
    ["Fig. 5.1: General System Flowchart", "12"],
    ["Fig. 5.2: Data Flow Diagram (Level 0)", "12"],
    ["Fig. 5.3: Web Application User Interface", "14"],
    ["Fig. A.1: Summarization function", "20"],
    ["Fig. A.2: OCR routing", "20"],
    ["Fig. A.3: Image summarization endpoint", "21"],
    ["Fig. A.4: Gemini vision client", "21"],
], widths=[13.5, 3.0])

# ---------------------------------------------------------------- LIST OF TABLES
doc.add_page_break()
para(doc, "LIST OF TABLES", size=14, bold=True, align="center", after=10)
table(doc, ["Table Title", "Page No."], [
    ["Table 2.1: Summary of Literature Review", "5"],
    ["Table 3.1: Functional Requirements", "6"],
    ["Table 3.2: Non-Functional Requirements", "7"],
    ["Table 3.3: Hardware Requirements", "7"],
    ["Table 3.4: Software Requirements", "8"],
    ["Table 4.1: Dataset Description", "11"],
    ["Table 5.1: Tools, Technologies and Libraries", "13"],
    ["Table 6.1: Functional Test Cases", "15"],
    ["Table 6.2: ROUGE Score Results", "16"],
], widths=[13.5, 3.0])

# ---------------------------------------------------------------- CHAPTER 1
chapter(doc, 1, "Introduction")
section(doc, "1.1", "Introduction to the Project:")
para(doc, "The amount of digital text available today is enormous. Long PDF documents, Word "
     "files, reports, and articles are used for education, news, research, business, and public "
     "administration. Reading every document completely is time-consuming, and important points "
     "can be difficult to locate quickly. A summarization system helps a reader understand the "
     "key ideas of a document in a short time.", style="Body Text", align="justify")
para(doc, "Multilingual Document Summarizer is an NLP-based application that generates "
     "abstractive summaries of documents and images in English and Hindi. Documents can be "
     "uploaded as .txt, .pdf, or .docx files, images can be uploaded as .png or .jpg, and users "
     "can also paste text directly.", style="Body Text", align="justify")
para(doc, "The extracted text is sent to a Transformer-based sequence-to-sequence model. English "
     "text is summarized using BART fine-tuned on CNN/DailyMail, and Hindi text using IndicBART "
     "fine-tuned on XL-Sum. The system is exposed through a web application built with FastAPI "
     "and an HTML/CSS/JavaScript frontend, and through a Streamlit demo.",
     style="Body Text", align="justify")

section(doc, "1.2", "Background and Motivation")
para(doc, "Digital technology has changed the way people read and share information. Documents "
     "are increasingly available online, and mobile cameras make it easy to capture text as "
     "images. Readers often need a quick understanding of a long document rather than a complete "
     "reading, which motivates automatic summarization.", style="Body Text", align="justify")
para(doc, "Language is another important consideration. Many readers in India are more "
     "comfortable reading Hindi than English, and most summarization tools support only English. "
     "Providing summaries in Hindi makes useful information accessible to a wider audience.",
     style="Body Text", align="justify")
para(doc, "Finally, a large amount of content is available only as images or scanned documents. "
     "Combining OCR with summarization allows such content to be handled by the same system.",
     style="Body Text", align="justify")

section(doc, "1.3", "Problem Statement")
para(doc, "To develop a multilingual NLP-based system that accepts documents and images, extracts "
     "their text (using OCR for images), and generates abstractive summaries in English and Hindi "
     "through a simple web interface, so that readers can understand long content quickly without "
     "being limited by language or input format.", style="Body Text", align="justify")

section(doc, "1.4", "Objectives")
para(doc, "The major objectives of the project are:", style="Body Text", after=2)
numbered(doc, [
    "To develop a system that summarizes long documents and images in English and Hindi.",
    "To implement OCR for extracting text from images.",
    "To fine-tune Transformer-based models (BART and IndicBART) for abstractive summarization.",
    "To support .txt, .pdf, .docx, and image inputs, as well as pasted text.",
    "To provide a clean web interface (FastAPI + HTML/CSS/JS) and a Streamlit demo.",
    "To evaluate the fine-tuned models using the ROUGE metric.",
    "To provide an optional Gemini API backend that runs without local models.",
])

section(doc, "1.5", "Scope of the Project")
para(doc, "The project focuses on building a working bilingual summarization tool. Its scope "
     "includes:", style="Body Text", after=2)
bullets(doc, [
    "Uploading .txt, .pdf, and .docx documents and extracting their text.",
    "Uploading .png/.jpg images and extracting text using OCR.",
    "Pasting text directly for summarization.",
    "Generating abstractive summaries in English and Hindi.",
    "Fine-tuning BART (English) and IndicBART (Hindi).",
    "Evaluating quality with ROUGE-1, ROUGE-2, ROUGE-L, and ROUGE-Lsum.",
    "A FastAPI web application, a Streamlit demo, and an optional Gemini backend.",
])
para(doc, "Summaries of very long documents are limited by the model's maximum input length.",
     style="Body Text", align="justify")

section(doc, "1.6", "Applications of the Project")
numbered(doc, [
    "Education: students can summarize long study material and scanned notes.",
    "News and Media: quick summaries of long articles in English or Hindi.",
    "Government and Administration: summarizing lengthy notices and reports.",
    "Accessibility: Hindi readers can access content in their own language.",
    "Research and Business: fast scanning of reports and documents.",
    "Digital Libraries: converting scanned pages and long PDFs into short summaries.",
])

# ---------------------------------------------------------------- CHAPTER 2
chapter(doc, 2, "Literature Review")
section(doc, "2.1", "Review of Existing Research Papers")
para(doc, "Natural Language Processing, abstractive summarization, Transformer models, and OCR "
     "are the main research areas related to this project.", style="Body Text", align="justify")
subsection(doc, "2.1.1 Attention Is All You Need")
para(doc, "Vaswani et al. (2017) introduced the Transformer architecture, which uses "
     "self-attention to model relationships between elements of a sequence. Transformers are the "
     "foundation of BART and IndicBART.", style="Body Text", align="justify")
subsection(doc, "2.1.2 BART: Denoising Sequence-to-Sequence Pre-training")
para(doc, "Lewis et al. (2019) introduced BART, a denoising autoencoder that combines "
     "bidirectional and autoregressive Transformers. BART is effective for abstractive "
     "summarization and bart-large-cnn is a standard baseline on CNN/DailyMail.",
     style="Body Text", align="justify")
subsection(doc, "2.1.3 IndicBART for Indian Languages")
para(doc, "Dabre et al. (2022) introduced IndicBART, a pre-trained sequence-to-sequence model for "
     "Indian languages. It uses a compact mBART-style architecture and a language-token format "
     "that allows fine-tuning for Hindi summarization.", style="Body Text", align="justify")
subsection(doc, "2.1.4 XL-Sum: Large-Scale Multilingual Abstractive Summarization")
para(doc, "Hasan et al. (2021) introduced XL-Sum, a multilingual dataset of news article and "
     "summary pairs covering 44 languages, including Hindi. It is used to fine-tune the Indic "
     "model.", style="Body Text", align="justify")
subsection(doc, "2.1.5 OCR for Text Extraction from Images")
para(doc, "Optical Character Recognition converts text in images into machine-readable text. "
     "EasyOCR is a deep-learning OCR library supporting English and Hindi, and modern vision "
     "models such as Gemini can also perform OCR.", style="Body Text", align="justify")
table(doc, ["Research / resource", "Main contribution", "Relevance"], [
    ["Vaswani et al. (2017)", "Transformer architecture", "Foundation of BART and IndicBART"],
    ["Lewis et al. (2019)", "BART denoising model", "English abstractive summarizer"],
    ["Dabre et al. (2022)", "IndicBART for Indian languages", "Hindi summarization"],
    ["Hasan et al. (2021)", "XL-Sum multilingual dataset", "Fine-tuning the Hindi model"],
    ["EasyOCR / Gemini", "OCR for images", "Text acquisition from images"],
], widths=[4.5, 5.0, 5.5], caption="Table 2.1: Summary of Literature Review")

section(doc, "2.2", "Existing System")
para(doc, "Existing summarization tools mostly target English text. They include cloud-based "
     "summarization APIs, browser extensions, and standalone applications. Some tools also support "
     "OCR, but text extraction and summarization are usually provided by separate systems.",
     style="Body Text", align="justify")
para(doc, "Indic summarization is less commonly available. Integrated document-and-image "
     "summarization for Hindi is not readily available to general users.",
     style="Body Text", align="justify")
section(doc, "2.3", "Limitations of Existing System")
numbered(doc, [
    "Most summarization tools support English only.",
    "Regional languages such as Hindi are poorly supported.",
    "Text extraction from images and summarization are usually separate tools.",
    "Uploading long documents in multiple formats is not always supported.",
    "Many tools require programming knowledge or paid API access.",
])
section(doc, "2.4", "Research Gap")
para(doc, "There is a need for a unified system that accepts both documents and images, supports "
     "English and Hindi, and provides summaries through a simple web interface. This project fills "
     "that gap by combining fine-tuned BART and IndicBART models, OCR, and a user-friendly web "
     "front-end in a single application.", style="Body Text", align="justify")

# ---------------------------------------------------------------- CHAPTER 3
chapter(doc, 3, "Problem Statement and Requirements")
section(doc, "3.1", "Problem Definition")
para(doc, "The problem addressed by the project is the difficulty readers face in quickly "
     "understanding long documents and images, especially when the content is in a regional "
     "language. A user requires a simple method to upload content, choose a language, and receive "
     "a short summary without installing machine-learning libraries.",
     style="Body Text", align="justify")
section(doc, "3.2", "Proposed Solution")
para(doc, "The user uploads a document or an image, or pastes text, and selects a language. The "
     "backend extracts the text, passes it to the summarization model, and returns the summary.",
     style="Body Text", align="justify")
para(doc, "The system uses Python and Hugging Face Transformers, with PyMuPDF and python-docx for "
     "text extraction and EasyOCR (or Gemini vision) for OCR. A Streamlit version and an optional "
     "Gemini API backend are also provided.", style="Body Text", align="justify")
section(doc, "3.3", "Functional Requirements")
table(doc, ["ID", "Requirement", "Description"], [
    ["FR01", "Upload document", "Accept .txt, .pdf, and .docx files"],
    ["FR02", "Upload image", "Accept .png and .jpg files"],
    ["FR03", "Text extraction", "Extract text from the document or image (OCR)"],
    ["FR04", "Language selection", "Allow the user to choose English or Hindi"],
    ["FR05", "Summarize text", "Generate an abstractive summary"],
    ["FR06", "Display result", "Show the summary and the extracted text"],
    ["FR07", "Download summary", "Allow the summary to be downloaded as a text file"],
    ["FR08", "Model selection", "Automatically use the fine-tuned model if available"],
    ["FR09", "Error handling", "Display friendly errors for unsupported or empty input"],
], widths=[1.6, 4.2, 9.2], caption="Table 3.1: Functional Requirements")
section(doc, "3.4", "Non-Functional Requirements")
table(doc, ["Requirement", "Description"], [
    ["Usability", "The interface should be simple and easy to navigate"],
    ["Performance", "Summaries should be generated in a reasonable time"],
    ["Reliability", "Valid inputs should produce a summary without crashing"],
    ["Maintainability", "Code should be organized into clear modules"],
    ["Scalability", "Additional languages and models should be easy to add"],
    ["Compatibility", "The web interface should work in modern browsers"],
    ["Data privacy", "Uploaded content should be processed securely"],
], widths=[4.5, 10.5], caption="Table 3.2: Non-Functional Requirements")
section(doc, "3.5", "Hardware and Software Requirements")
table(doc, ["Component", "Requirement"], [
    ["Processor", "Intel Core i5 or equivalent (Apple M-series supported)"],
    ["RAM", "8 GB minimum; 16 GB recommended for model loading"],
    ["Storage", "Approximately 5 GB for models and dependencies"],
    ["Display", "Standard laptop or desktop display"],
    ["Network", "Internet required for the first model download"],
], widths=[6.0, 9.0], caption="Table 3.3: Hardware Requirements")
table(doc, ["Software", "Purpose"], [
    ["Python 3.10+", "Programming language"],
    ["PyTorch", "Deep-learning backend"],
    ["Hugging Face Transformers", "BART and IndicBART models"],
    ["Hugging Face Datasets", "CNN/DailyMail and XL-Sum"],
    ["EasyOCR", "Optical Character Recognition"],
    ["PyMuPDF / python-docx", "PDF and DOCX text extraction"],
    ["FastAPI + Uvicorn", "Web backend"],
    ["Streamlit", "Demo interface"],
    ["HTML / CSS / JavaScript", "Web frontend"],
    ["Evaluate / rouge_score", "ROUGE evaluation"],
    ["Google Gemini API (optional)", "Hosted text + vision backend"],
], widths=[6.0, 9.0], caption="Table 3.4: Software Requirements")

# ---------------------------------------------------------------- CHAPTER 4
chapter(doc, 4, "Proposed Methodology")
section(doc, "4.1", "Overview of the Proposed System")
para(doc, "The frontend sends the uploaded file or pasted text and the selected language to the "
     "backend. The backend performs text extraction, selects the appropriate model, generates a "
     "summary, and returns it to the frontend.", style="Body Text", align="justify")
numbered(doc, [
    "Frontend: upload interface, language selection, and result display.",
    "Text extraction: PDF, DOCX, TXT parsing, and OCR for images.",
    "Summarization: language-specific BART or IndicBART inference (or the Gemini API).",
    "Training pipeline: fine-tuning scripts and the Kaggle notebooks.",
])
section(doc, "4.2", "System Architecture")
numbered(doc, [
    "Presentation layer: HTML/CSS/JavaScript (FastAPI) and Streamlit.",
    "Extraction layer: PyMuPDF, python-docx, and EasyOCR / Gemini vision.",
    "Model layer: BART (English) and IndicBART (Hindi), loaded from models/ if present.",
    "Optional API layer: Google Gemini, used when a Gemini key is configured.",
    "Training layer: Kaggle notebooks and scripts/train.py.",
])
para(doc, "For Hindi, the input is formatted as \u201c<text> </s> <2hi>\u201d and the decoder is "
     "forced to start with the language token, as required by IndicBART.",
     style="Body Text", align="justify")
section(doc, "4.3", "Workflow of the System")
numbered(doc, [
    "The user opens the web application.",
    "The user uploads a document/image or pastes text and selects a language.",
    "The backend extracts text using the appropriate extractor or OCR.",
    "The text is passed to the language-specific model (or the Gemini API).",
    "The model generates an abstractive summary using beam search.",
    "The summary and extracted text are returned to the frontend.",
    "The user can copy or download the summary.",
])

section(doc, "4.4", "NLP Techniques and Algorithms")
para(doc, "Natural Language Processing is used at every stage of this project. The following "
     "sub-sections describe each NLP technique and where it is applied.",
     style="Body Text", align="justify")
subsection(doc, "4.4.1 Text Preprocessing and Tokenization")
para(doc, "Raw text is cleaned and split into sub-word tokens using the BART and IndicBART "
     "tokenizers. Tokenization converts human-readable text into the integer token ids that the "
     "model processes, and truncation ensures the input fits the model's maximum length.",
     style="Body Text", align="justify")
subsection(doc, "4.4.2 Sequence-to-Sequence Abstractive Summarization")
para(doc, "The core NLP task is abstractive summarization. An encoder reads the input document "
     "and a decoder generates a new, shorter text that captures the main ideas. BART is used for "
     "English and IndicBART for Hindi, after fine-tuning on summarization datasets.",
     style="Body Text", align="justify")
subsection(doc, "4.4.3 Beam Search Decoding")
para(doc, "Summaries are generated token-by-token using beam search (num_beams = 4-5), combined "
     "with no-repeat n-gram constraints and length penalties. This produces fluent summaries "
     "while avoiding repetition and controlling length.", style="Body Text", align="justify")
subsection(doc, "4.4.4 Indic Language Handling")
para(doc, "IndicBART uses language tokens. The input is appended with \u201c</s>\u201d and a "
     "language token such as <2hi>, the target is prefixed with the same token, and the decoder "
     "start token is forced to it. This ensures that the generated summary is in Devanagari and in "
     "the correct language.", style="Body Text", align="justify")
subsection(doc, "4.4.5 OCR as an NLP Text-Acquisition Step")
para(doc, "Images are first converted into text using OCR. EasyOCR is used in local mode, and "
     "Gemini vision is used in the cloud backend. The recognized text then enters the same NLP "
     "summarization pipeline as a normal document.", style="Body Text", align="justify")
subsection(doc, "4.4.6 Evaluation with ROUGE")
para(doc, "Model quality is measured with ROUGE, which compares the generated summary with a "
     "reference summary using unigram overlap (ROUGE-1), bigram overlap (ROUGE-2), and longest "
     "common subsequence (ROUGE-L / ROUGE-Lsum).", style="Body Text", align="justify")
subsection(doc, "4.4.7 Summary: Role of NLP in the Project")
bullets(doc, [
    "Tokenization converts documents into model-readable token sequences.",
    "Sequence-to-sequence models perform abstractive summarization in English and Hindi.",
    "Beam search and n-gram constraints control the quality and length of generated text.",
    "IndicBART language tokens enable correct Devanagari output for Hindi.",
    "OCR supplies text from images so that it can be processed by the NLP pipeline.",
    "ROUGE provides a quantitative measure of summary quality.",
    "Fine-tuning adapts large pre-trained language models to the summarization task.",
])

section(doc, "4.5", "Dataset Collection and Preprocessing")
para(doc, "The project uses two public datasets:", style="Body Text", after=2)
bullets(doc, [
    "CNN/DailyMail (English): news articles paired with human-written highlights.",
    "XL-Sum (Hindi): news articles paired with summaries.",
])
para(doc, "XL-Sum is distributed as a script-based dataset, which newer versions of the Datasets "
     "library no longer support, so the project loads the auto-converted Parquet shards directly. "
     "Preprocessing includes tokenization, truncation, and, for IndicBART, language-token "
     "formatting.", style="Body Text", align="justify")
table(doc, ["Dataset", "Language", "Task", "Usage"], [
    ["CNN/DailyMail", "English", "News summarization", "Fine-tuning BART"],
    ["XL-Sum (hindi)", "Hindi", "News summarization", "Fine-tuning IndicBART"],
], widths=[4.0, 3.0, 4.5, 3.5], caption="Table 4.1: Dataset Description")

# ---------------------------------------------------------------- CHAPTER 5
chapter(doc, 5, "System Design and Implementation")
section(doc, "5.1", "System Design")
para(doc, "The system is divided into independent modules to simplify development and "
     "maintenance.", style="Body Text", align="justify")
bullets(doc, [
    "Input and upload interface.",
    "Document text extraction (PyMuPDF, python-docx).",
    "Image text extraction (EasyOCR / Gemini vision).",
    "Language-aware summarization (BART / IndicBART).",
    "Optional Gemini API backend.",
    "Web API layer (FastAPI) and Streamlit demo.",
])
para(doc, "The modules share a common src/ package, so the web app, Streamlit demo, and training "
     "script use the same inference code.", style="Body Text", align="justify")
section(doc, "5.2", "Flowchart / UML / DFD Diagrams")
para(doc, "The following diagrams describe the proposed system. They can be inserted using "
     "draw.io, Microsoft Word Shapes, or another diagram tool.", style="Body Text", align="justify")
subsection(doc, "5.2.1 General System Flowchart")
para(doc, "Upload \u2192 text extraction / OCR \u2192 language selection \u2192 model inference "
     "\u2192 summary \u2192 display/download.", style="Body Text", align="justify")
para(doc, "Figure 5.1: General workflow of the bilingual summarization system.",
     size=10, italic=True, align="center")
subsection(doc, "5.2.2 Data Flow Diagram (Level 0)")
para(doc, "The user provides a document or image and a language; the system returns a summary. "
     "The model, OCR, and text-extraction components are internal processes.",
     style="Body Text", align="justify")
para(doc, "Figure 5.2: Level 0 Data Flow Diagram.", size=10, italic=True, align="center")
section(doc, "5.3", "Tools, Technologies and Libraries")
table(doc, ["Technology", "Application"], [
    ["Python", "Core programming language"],
    ["PyTorch", "Deep-learning backend"],
    ["Hugging Face Transformers", "BART and IndicBART models"],
    ["Hugging Face Datasets", "CNN/DailyMail and XL-Sum loading"],
    ["EasyOCR", "Image text extraction (local)"],
    ["PyMuPDF", "PDF text extraction"],
    ["python-docx", "DOCX text extraction"],
    ["FastAPI + Uvicorn", "Web backend"],
    ["Streamlit", "Demo interface"],
    ["HTML / CSS / JavaScript", "Web frontend"],
    ["Evaluate / rouge_score", "ROUGE evaluation"],
    ["Google Gemini API (optional)", "Hosted text + vision backend"],
], widths=[6.0, 9.0], caption="Table 5.1: Tools, Technologies and Libraries")
section(doc, "5.4", "Implementation Details")
subsection(doc, "5.4.1 Inference Core (src/)")
para(doc, "config.py defines the model registry, provider selection, and cache handling. "
     "text_extraction.py extracts text from .txt, .pdf, and .docx. ocr.py extracts text from "
     "images using EasyOCR or Gemini vision. summarizer.py loads the language-specific model and "
     "generates the summary, and llm_api.py implements the Gemini REST client.",
     style="Body Text", align="justify")
subsection(doc, "5.4.2 Web Application")
para(doc, "The FastAPI backend (web/server.py) exposes endpoints for text, document, and image "
     "summarization and serves the static frontend (web/static/), which provides drag-and-drop "
     "upload, language and length controls, and copy/download actions.",
     style="Body Text", align="justify")
subsection(doc, "5.4.3 Streamlit Demo")
para(doc, "app.py provides the same functionality through a sidebar-driven Streamlit interface "
     "with Document, Image, and Text modes.", style="Body Text", align="justify")
subsection(doc, "5.4.4 Training Pipeline")
para(doc, "The models are fine-tuned with scripts/train.py and the notebooks in notebooks/. "
     "Training uses the Hugging Face Seq2SeqTrainer, and evaluation uses ROUGE-1, ROUGE-2, "
     "ROUGE-L, and ROUGE-Lsum.", style="Body Text", align="justify")
section(doc, "5.5", "User Interface and Screenshots")
para(doc, "The web application provides a clean interface for uploading documents and images and "
     "for selecting the summary language. A screenshot of the running application is shown below.",
     style="Body Text", align="justify")
if SCREENSHOT.exists():
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(SCREENSHOT), width=Cm(15.5))
para(doc, "Figure 5.3: Web Application User Interface", size=10, italic=True, align="center")

# ---------------------------------------------------------------- CHAPTER 6
chapter(doc, 6, "Results and Discussion")
section(doc, "6.1", "Experimental Setup")
para(doc, "The models were fine-tuned on a Kaggle NVIDIA T4 GPU. BART-base was fine-tuned on "
     "CNN/DailyMail and IndicBART on the Hindi subset of XL-Sum. For each language, 2,000 training "
     "examples and 200 validation examples were used for two epochs, with a batch size of 4 and a "
     "learning rate of 3e-5. Summaries were generated with beam search and evaluated with ROUGE.",
     style="Body Text", align="justify")
section(doc, "6.2", "Test Cases and Sample Outputs")
table(doc, ["Test ID", "Input / Action", "Expected output"], [
    ["TC01", "Open the web application", "Upload interface is displayed"],
    ["TC02", "Upload a valid .txt file", "Text is extracted and shown"],
    ["TC03", "Upload a valid .pdf file", "Text is extracted and shown"],
    ["TC04", "Upload a valid .docx file", "Text is extracted and shown"],
    ["TC05", "Upload a valid image", "OCR text is extracted and shown"],
    ["TC06", "Paste text and summarize", "Summary is generated"],
    ["TC07", "Select English and summarize", "English summary is generated"],
    ["TC08", "Select Hindi and summarize", "Hindi summary is generated"],
    ["TC09", "Upload an empty/unsupported file", "A friendly error is shown"],
    ["TC10", "Download the summary", "A .txt file is downloaded"],
], widths=[1.6, 6.4, 7.0], caption="Table 6.1: Functional Test Cases")
section(doc, "6.3", "Performance Evaluation Metrics")
bullets(doc, [
    "ROUGE-1: unigram overlap between the generated and reference summaries.",
    "ROUGE-2: bigram overlap.",
    "ROUGE-L: longest common subsequence.",
    "ROUGE-Lsum: sentence-level longest common subsequence.",
])
section(doc, "6.4", "Results and Observations")
para(doc, "The fine-tuned models produced the following validation results:",
     style="Body Text", after=2)
table(doc, ["Language", "Model", "ROUGE-1", "ROUGE-2", "ROUGE-L", "ROUGE-Lsum"], [
    ["English", "BART-base (CNN/DailyMail)", "40.65", "19.10", "28.30", "37.59"],
    ["Hindi", "IndicBART (XL-Sum)", "60.42", "25.90", "60.36", "60.26"],
], widths=[2.4, 4.6, 1.9, 1.9, 1.9, 2.3], caption="Table 6.2: ROUGE Score Results")
para(doc, "The English model produced concise and relevant summaries. The Hindi model produced "
     "coherent summaries in the Devanagari script. Because only 2,000 examples were used, the "
     "Hindi model tends to be verbose and occasionally repeats phrases; this can be improved with "
     "more training data.", style="Body Text", align="justify")
para(doc, "The application was verified end-to-end: documents and images were uploaded, text was "
     "extracted (including OCR), and summaries were generated in both languages. Fine-tuned "
     "weights placed in models/ are detected automatically and used instead of the public "
     "checkpoints.", style="Body Text", align="justify")
section(doc, "6.5", "Limitations")
numbered(doc, [
    "The Hindi model was fine-tuned on a small sample and can be verbose.",
    "Very long documents exceed the model's maximum input length and are truncated.",
    "OCR accuracy depends on image quality and font rendering.",
    "The local models require a ~2 GB download on first use.",
    "The system runs on CPU by default; GPU improves speed.",
])

# ---------------------------------------------------------------- CHAPTER 7
chapter(doc, 7, "Conclusion and Future Scope")
section(doc, "7.1", "Conclusion")
para(doc, "Multilingual Document Summarizer is an NLP-based application that makes long documents "
     "and images easier to understand in English and Hindi. The project integrates text extraction "
     "(PDF, DOCX, TXT), OCR, abstractive summarization using BART and IndicBART, a FastAPI web "
     "application, and a Streamlit demo.", style="Body Text", align="justify")
para(doc, "The models were fine-tuned on Kaggle GPUs and evaluated using ROUGE. The English model "
     "achieved a ROUGE-1 of 40.65 and the Hindi model 60.42, showing that the approach is "
     "practical. The project demonstrates how NLP, OCR, and web technologies can be combined to "
     "build a useful bilingual tool.", style="Body Text", align="justify")
section(doc, "7.2", "Future Scope")
numbered(doc, [
    "Fine-tune on the full datasets and more epochs for higher-quality summaries.",
    "Add chunking and hierarchical summarization for very long documents.",
    "Support additional Indian languages and scripts.",
    "Improve the Hindi model to reduce repetition and verbosity.",
    "Add voice input and text-to-speech for accessibility.",
    "Deploy the application on a public server with authentication.",
])

# ---------------------------------------------------------------- REFERENCES
doc.add_page_break()
para(doc, "REFERENCES", size=14, bold=True, align="center", after=12)
numbered(doc, [
    "Lewis, M., et al. (2019). \u201cBART: Denoising Sequence-to-Sequence Pre-training.\u201d arXiv:1910.13461.",
    "Dabre, R., et al. (2022). \u201cIndicBART: A Pre-trained Model for Natural Language Generation of Indic Languages.\u201d arXiv:2109.02903.",
    "Hasan, T., et al. (2021). \u201cXL-Sum: Large-Scale Multilingual Abstractive Summarization for 44 Languages.\u201d Findings of ACL-IJCNLP 2021.",
    "Vaswani, A., et al. (2017). \u201cAttention Is All You Need.\u201d Advances in Neural Information Processing Systems.",
    "Hermann, K. M., et al. (2015). \u201cTeaching Machines to Read and Comprehend.\u201d NeurIPS. (CNN/DailyMail)",
    "EasyOCR. https://github.com/JaidedAI/EasyOCR",
    "Hugging Face Transformers. https://huggingface.co/docs/transformers/",
    "PyMuPDF Documentation. https://pymupdf.readthedocs.io/",
    "FastAPI Documentation. https://fastapi.tiangolo.com/",
    "Streamlit Documentation. https://docs.streamlit.io/",
    "Google Gemini API. https://ai.google.dev/",
])

# ---------------------------------------------------------------- APPENDIX A
doc.add_page_break()
para(doc, "APPENDIX A: IMPORTANT CODE SNIPPETS", size=14, bold=True, align="center", after=10)
para(doc, "This appendix presents the core code modules of the project as editor screenshots, "
     "followed by a short description of each.", style="Body Text", align="justify")

CODE_DIR = ROOT / "report" / "code_screenshots"


def code_image(doc, filename, caption):
    path = CODE_DIR / filename
    if path.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(path), width=Cm(15.0))
    para(doc, caption, size=10, italic=True, align="center")


subsection(doc, "A.1 Summarization Function")
para(doc, "Source file: src/summarizer.py", size=10, italic=True)
code_image(doc, "01_summarizer.png", "Figure A.1: Summarization function (src/summarizer.py)")
para(doc, "Description: The summarize() function is the single entry point for every "
     "summarization request. It first checks the configured backend: when SUMMARY_PROVIDER is "
     "\u201cgemini\u201d it delegates to summarize_with_gemini() and returns the result. "
     "Otherwise, it loads the language-specific tokenizer and model, builds the generation "
     "settings (beam search, length limits, no-repeat n-grams), tokenizes and truncates the input, "
     "applies the IndicBART language-token format for Hindi, calls model.generate(), and decodes "
     "the output while stripping control tokens. The same function therefore serves both the "
     "FastAPI web application and the Streamlit demo.", style="Body Text", align="justify")

subsection(doc, "A.2 OCR Routing")
para(doc, "Source file: src/ocr.py", size=10, italic=True)
code_image(doc, "02_ocr.png", "Figure A.2: OCR routing (src/ocr.py)")
para(doc, "Description: image_to_text_any() abstracts over two OCR backends. In Gemini mode it "
     "forwards the raw image bytes to extract_text_with_gemini(), so no local OCR model is needed "
     "in the cloud deployment. In local mode it converts the bytes into a PIL image and calls "
     "image_to_text(), which runs EasyOCR for English and Hindi. This keeps the same UI code "
     "working in both the lightweight cloud build and the full local installation.",
     style="Body Text", align="justify")

subsection(doc, "A.3 Image Summarization Endpoint")
para(doc, "Source file: web/server.py", size=10, italic=True)
code_image(doc, "03_api.png", "Figure A.3: Image summarization endpoint (web/server.py)")
para(doc, "Description: The /api/ocr-summarize endpoint accepts a multipart image upload together "
     "with the target language and length limits. It validates the language, reads the image "
     "bytes, extracts the text with image_to_text_any(), rejects the request when no text is "
     "detected, and then summarizes the extracted text. The response returns both the summary and "
     "the OCR text so the frontend can display them.", style="Body Text", align="justify")

subsection(doc, "A.4 Gemini Vision Client")
para(doc, "Source file: src/llm_api.py", size=10, italic=True)
code_image(doc, "04_gemini.png", "Figure A.4: Gemini vision OCR client (src/llm_api.py)")
para(doc, "Description: extract_text_with_gemini() implements OCR through Gemini's multimodal "
     "API. It builds an extraction prompt, base64-encodes the image, and sends it as inline image "
     "data with the correct MIME type. The shared _generate() helper posts the request to the "
     "Gemini REST endpoint and returns the recognized text, which is then passed to the "
     "summarization step.", style="Body Text", align="justify")

# ---------------------------------------------------------------- APPENDIX B
doc.add_page_break()
para(doc, "APPENDIX B: ADDITIONAL SCREENSHOTS / OUTPUTS", size=14, bold=True, align="center", after=10)
para(doc, "Sample outputs generated by the system are shown below.", style="Body Text", align="justify")
table(doc, ["Language", "Input (excerpt)", "Generated summary (excerpt)"], [
    ["English", "Artificial intelligence is transforming many industries\u2026",
     "Machine learning models can now read documents and images."],
    ["Hindi", "\u092d\u093e\u0930\u0924 \u0938\u0930\u0915\u093e\u0930 \u0928\u0947 "
     "\u0921\u093f\u091c\u093f\u091f\u0932 \u0936\u093f\u0915\u094d\u0937\u093e \u0915\u094b "
     "\u092c\u0922\u093c\u093e\u0935\u093e \u0926\u0947\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f "
     "\u092f\u094b\u091c\u0928\u093e\u2026",
     "\u092d\u093e\u0930\u0924 \u0938\u0930\u0915\u093e\u0930 \u0928\u0947 "
     "\u0928\u0908 \u092f\u094b\u091c\u0928\u093e \u0915\u0940 \u0918\u094b\u0937\u0923\u093e "
     "\u0915\u0940 \u0939\u0948\u0964"],
], widths=[2.2, 6.4, 6.4], caption="Table B.1: Sample Outputs")
para(doc, "OCR sample:", style="Body Text", bold=True, after=2)
para(doc, "Input image (synthetic): \u201cHello from the OCR test document.\u201d",
     style="Body Text", align="justify")
para(doc, "OCR output: \u201cHello from the OCR test document.\u201d", style="Body Text", align="justify")
para(doc, "Generated summary: \u201cThis is an OCR test document.\u201d",
     style="Body Text", align="justify")

doc.save(OUT)
check = Document(OUT)
print("saved:", OUT)
print("paragraphs:", len(check.paragraphs), "| tables:", len(check.tables))
