"""Build the Mini Project Report (AISSMS format) for the
Multilingual Document Summarizer project (English + Hindi, no OCR)."""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

ROOT = Path(__file__).resolve().parent.parent
SCREENSHOT = ROOT / "docs" / "screenshot.png"
OUT = ROOT / "report" / "Mini_Project_Report_Multilingual_Summarizer.docx"

FONT = "Times New Roman"


def base_document() -> Document:
    doc = Document()
    sec = doc.sections[0]
    sec.page_height = Cm(29.7)
    sec.page_width = Cm(21.0)
    sec.top_margin = Cm(2.2)
    sec.bottom_margin = Cm(2.0)
    sec.left_margin = Cm(2.2)
    sec.right_margin = Cm(1.8)

    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(11)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.15

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


def para(doc, text, size=11, bold=False, italic=False, align="left", before=0, after=6):
    p = doc.add_paragraph()
    p.alignment = {
        "left": WD_ALIGN_PARAGRAPH.LEFT,
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "right": WD_ALIGN_PARAGRAPH.RIGHT,
        "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
    }[align]
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    r = p.add_run(text)
    r.bold = bold
    r.italic = italic
    r.font.size = Pt(size)
    r.font.name = FONT
    return p


def chapter_title(doc, number, title):
    doc.add_page_break()
    para(doc, f"CHAPTER {number}", size=14, bold=True, align="center", after=2)
    para(doc, title.upper(), size=14, bold=True, align="center", after=12)


def section(doc, number, title):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(f"{number} {title}")
    r.bold = True
    r.font.size = Pt(12)
    r.font.name = FONT


def subsection(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text)
    r.bold = True
    r.font.size = Pt(11)
    r.font.name = FONT


def shade(cell, hex_color="DCE6F1"):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tc_pr.append(shd)


def table(doc, headers, rows, widths=None, caption=None):
    if caption:
        para(doc, caption, size=10, bold=True, before=8, after=4)
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        p = hdr[i].paragraphs[0]
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(10)
        r.font.name = FONT
        shade(hdr[i])
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            p = cells[i].paragraphs[0]
            r = p.add_run(str(val))
            r.font.size = Pt(10)
            r.font.name = FONT
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def bullets(doc, items):
    for it in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(it)
        r.font.size = Pt(11)
        r.font.name = FONT


def numbered(doc, items):
    for i, it in enumerate(items, 1):
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.6)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(f"{i}. ")
        r.bold = True
        r.font.size = Pt(11)
        r.font.name = FONT
        r2 = p.add_run(it)
        r2.font.size = Pt(11)
        r2.font.name = FONT


doc = base_document()

# TITLE PAGE
para(doc, "", after=10)
para(doc, "A Mini Project Report", size=16, bold=True, align="center", after=6)
para(doc, "on", size=11, align="center", after=6)
para(doc, "Multilingual Document Summarizer", size=20, bold=True, align="center", after=18)
para(doc, "Submitted to", size=11, align="center", after=2)
para(doc, "AISSMS College of Engineering, Pune", size=12, bold=True, align="center", after=10)
para(doc, "In partial fulfillment of the requirements for the Third Year of the Degree of", size=10, align="center", after=2)
para(doc, "BE/BTech", size=11, bold=True, align="center", after=2)
para(doc, "in", size=10, align="center", after=2)
para(doc, "Artificial Intelligence and Machine Learning", size=11, bold=True, align="center", after=14)
para(doc, "Submitted by", size=11, align="center", after=2)
para(doc, "1. Hardik Pathak  –  ______________", size=11, align="center", after=2)
para(doc, "2. ______________________________", size=11, align="center", after=2)
para(doc, "3. ______________________________", size=11, align="center", after=14)
para(doc, "Under the guidance of", size=11, align="center", after=2)
para(doc, "Prof. ______________________", size=11, bold=True, align="center", after=16)
para(doc, "Department of Artificial Intelligence and Machine Learning", size=11, bold=True, align="center", after=2)
para(doc, "AISSMS College of Engineering", size=12, bold=True, align="center", after=2)
para(doc, "Kennedy Road, Pune – 411001, Maharashtra, India", size=10, align="center", after=14)
para(doc, "Academic Year: 2026–2027", size=11, bold=True, align="center")

# CERTIFICATE
doc.add_page_break()
para(doc, "CERTIFICATE", size=14, bold=True, align="center", after=14)
para(doc, "This is to certify that the project report entitled \u201cMultilingual Document Summarizer\u201d "
     "is a record of bonafide work carried out by the students under the supervision and guidance of "
     "Prof. ____________________, in partial fulfillment of the requirements for the Third Year "
     "(Artificial Intelligence and Machine Learning) programme of AISSMS College of Engineering, Pune, "
     "during the academic year 2026–2027.", align="justify", after=16)
para(doc, "Date:", size=11, after=2)
para(doc, "Place: Pune", size=11, after=28)
para(doc, "Submitted by:", size=11, bold=True, after=2)
para(doc, "1. Hardik Pathak  –  ______________", size=11, after=2)
para(doc, "2. ______________________________", size=11, after=2)
para(doc, "3. ______________________________", size=11, after=24)
para(doc, "____________________\t\t\t____________________", size=11, after=0)
para(doc, "Prof. ________________    \t\t\tDr. ________________", size=10, after=0)
para(doc, "Project Guide\t\t\t\tHead of Department", size=10)

# ACKNOWLEDGEMENT
doc.add_page_break()
para(doc, "ACKNOWLEDGEMENT", size=14, bold=True, align="center", after=14)
para(doc, "We would like to express our sincere gratitude to our project guide for providing valuable "
     "guidance, encouragement, and support throughout the development of our mini project, "
     "\u201cMultilingual Document Summarizer\u201d. Their valuable suggestions, constructive feedback, "
     "and continuous motivation helped us understand the project requirements and complete the work "
     "successfully.", align="justify")
para(doc, "We are thankful to our Head of Department and all faculty members for giving us the "
     "opportunity to work on this project as part of our Natural Language Processing (NLP) curriculum. "
     "Their guidance and support encouraged us to explore the practical applications of NLP and "
     "understand how modern sequence-to-sequence models can be used to solve real-world problems.",
     align="justify")
para(doc, "We would also like to extend our sincere thanks to our college for providing the necessary "
     "facilities, resources, and a positive learning environment throughout the project development "
     "process.", align="justify")
para(doc, "Through this project, we gained practical experience in text preprocessing, abstractive "
     "summarization using Transformer-based models (BART and IndicBART), model fine-tuning on Kaggle "
     "GPUs, ROUGE-based evaluation, and web application development using Python, FastAPI, and "
     "Streamlit.", align="justify")
para(doc, "We would also like to acknowledge the learning resources, technical documentation, and "
     "open-source datasets and models (CNN/DailyMail, XL-Sum, Hugging Face Transformers) that helped "
     "us understand the tools and technologies used in this project.", align="justify")
para(doc, "Finally, we are thankful to everyone who directly or indirectly supported us during the "
     "completion of this mini project. This experience helped us understand the importance of making "
     "information accessible across languages, and we hope that the system can contribute towards "
     "easier access to long documents for readers of English and Hindi.", align="justify")

# ABSTRACT
doc.add_page_break()
para(doc, "ABSTRACT", size=14, bold=True, align="center", after=14)
para(doc, "Multilingual Document Summarizer is a web-based application that produces concise, "
     "abstractive summaries of long documents in English and Hindi. Large amounts of useful "
     "information are locked inside PDF files, Word documents, and plain-text files, and readers "
     "often need to spend considerable time locating the key points. Language is an additional "
     "barrier, because most existing summarization tools support English only.", align="justify")
para(doc, "The proposed system accepts .txt, .pdf, and .docx files, extracts their text, and passes "
     "it to a language-specific sequence-to-sequence model that generates an abstractive summary. "
     "English documents are summarized using BART fine-tuned on the CNN/DailyMail dataset, while "
     "Hindi documents are summarized using IndicBART fine-tuned on the XL-Sum dataset. Users can also "
     "paste text directly for summarization.", align="justify")
para(doc, "The application is developed using Python and the Hugging Face Transformers library, with "
     "text extraction handled by PyMuPDF and python-docx. The user interface is provided in two forms: "
     "a FastAPI-backed web application with an HTML/CSS/JavaScript frontend, and a Streamlit demo. The "
     "models were fine-tuned on a NVIDIA T4 GPU using the Hugging Face Trainer and evaluated using the "
     "ROUGE metric. An optional Gemini API backend allows the app to run without downloading local "
     "models.", align="justify")
para(doc, "Keywords: Natural Language Processing (NLP), Abstractive Summarization, BART, IndicBART, "
     "XL-Sum, Multilingual, Fine-tuning, ROUGE, FastAPI, Streamlit.", size=10, italic=True,
     align="justify")

# CONTENT
doc.add_page_break()
para(doc, "CONTENT", size=14, bold=True, align="center", after=12)
table(doc, ["Chapter / Contents", "Page No."], [
    ["Acknowledgement", "i"], ["Abstract", "ii"], ["Table of Contents", "iii"],
    ["List of Figures", "iv"], ["List of Tables", "v"],
    ["Chapter 1: Introduction", "1"], ["1.1 Introduction to the Project", "1"],
    ["1.2 Background and Motivation", "1"], ["1.3 Problem Statement", "2"],
    ["1.4 Objectives", "2"], ["1.5 Scope of the Project", "2"],
    ["1.6 Applications of the Project", "3"],
    ["Chapter 2: Literature Review", "4"], ["2.1 Review of Existing Research Papers", "4"],
    ["2.2 Existing System", "5"], ["2.3 Limitations of Existing System", "5"],
    ["2.4 Research Gap", "5"],
    ["Chapter 3: Problem Statement and Requirements", "6"], ["3.1 Problem Definition", "6"],
    ["3.2 Proposed Solution", "6"], ["3.3 Functional Requirements", "6"],
    ["3.4 Non-Functional Requirements", "7"], ["3.5 Hardware and Software Requirements", "7"],
    ["Chapter 4: Proposed Methodology", "8"], ["4.1 Overview of the Proposed System", "8"],
    ["4.2 System Architecture", "8"], ["4.3 Workflow of the System", "9"],
    ["4.4 NLP Techniques and Algorithms", "9"], ["4.5 Dataset Collection and Preprocessing", "10"],
    ["Chapter 5: System Design and Implementation", "11"], ["5.1 System Design", "11"],
    ["5.2 Flowchart / UML / DFD Diagrams", "11"], ["5.3 Tools, Technologies and Libraries", "12"],
    ["5.4 Implementation Details", "12"], ["5.5 User Interface and Screenshots", "13"],
    ["Chapter 6: Results and Discussion", "14"], ["6.1 Experimental Setup", "14"],
    ["6.2 Test Cases and Sample Outputs", "14"], ["6.3 Performance Evaluation Metrics", "15"],
    ["6.4 Results and Observations", "15"], ["6.5 Limitations", "16"],
    ["Chapter 7: Conclusion and Future Scope", "17"], ["7.1 Conclusion", "17"],
    ["7.2 Future Scope", "17"], ["References", "18"],
    ["Appendix A: Important Code Snippets", "19"],
    ["Appendix B: Additional Screenshots / Outputs", "20"],
], widths=[14.0, 2.5])

# LIST OF FIGURES
doc.add_page_break()
para(doc, "LIST OF FIGURES", size=14, bold=True, align="center", after=12)
table(doc, ["Figure Title", "Page No."], [
    ["Fig. 1.1: Overview of the Summarization Pipeline", "3"],
    ["Fig. 2.1: Existing Summarization Workflow", "6"],
    ["Fig. 4.1: Proposed System Architecture", "8"],
    ["Fig. 4.2: Workflow of the Proposed System", "9"],
    ["Fig. 5.1: General System Flowchart", "11"],
    ["Fig. 5.2: Data Flow Diagram (Level 0)", "12"],
    ["Fig. 5.3: Web Application User Interface", "13"],
], widths=[13.5, 3.0])

# LIST OF TABLES
doc.add_page_break()
para(doc, "LIST OF TABLES", size=14, bold=True, align="center", after=12)
table(doc, ["Table Title", "Page No."], [
    ["Table 2.1: Summary of Literature Review", "5"],
    ["Table 3.1: Functional Requirements", "6"],
    ["Table 3.2: Non-Functional Requirements", "7"],
    ["Table 3.3: Hardware and Software Requirements", "7"],
    ["Table 4.1: Dataset Description", "10"],
    ["Table 5.1: Tools, Technologies and Libraries Used", "12"],
    ["Table 6.1: Functional Test Cases", "14"],
    ["Table 6.2: ROUGE Score Results", "15"],
], widths=[13.5, 3.0])

# CHAPTER 1
chapter_title(doc, 1, "Introduction")
section(doc, "1.1", "Introduction to the Project:")
para(doc, "The amount of digital text available today is enormous. Long PDF documents, Word files, "
     "reports, and articles are used for education, news, research, business, and public "
     "administration. Reading every document completely is time-consuming, and important points can "
     "be difficult to locate quickly. A summarization system helps a reader understand the key ideas "
     "of a document in a short time.", align="justify")
para(doc, "Multilingual Document Summarizer is an NLP-based application that generates abstractive "
     "summaries of documents in English and Hindi. Documents can be uploaded as .txt, .pdf, or .docx "
     "files, and users can also paste text directly.", align="justify")
para(doc, "The extracted text is sent to a Transformer-based sequence-to-sequence model. English "
     "text is summarized using BART fine-tuned on CNN/DailyMail, and Hindi text is summarized using "
     "IndicBART fine-tuned on XL-Sum. The system is exposed through a web application built with "
     "FastAPI and an HTML/CSS/JavaScript frontend, and through a Streamlit demo.", align="justify")
section(doc, "1.2", "Background and Motivation")
para(doc, "Digital technology has changed the way people read and share information. Documents are "
     "increasingly available online, yet readers often need a quick understanding of a long document "
     "rather than a complete reading, which motivates automatic summarization.", align="justify")
para(doc, "Language is another important consideration. Many readers in India are more comfortable "
     "reading Hindi than English, and most summarization tools support only English. Providing "
     "summaries in Hindi makes useful information accessible to a wider audience, and fine-tuned "
     "multilingual models such as IndicBART make this practical.", align="justify")
section(doc, "1.3", "Problem Statement")
para(doc, "To develop a multilingual NLP-based system that accepts documents, extracts their text, "
     "and generates abstractive summaries in English and Hindi through a simple web interface, so "
     "that readers can understand long content quickly without being limited by language.",
     align="justify")
section(doc, "1.4", "Objectives")
para(doc, "The major objectives of the project are:", after=2)
numbered(doc, [
    "To develop a system that summarizes long documents in English and Hindi.",
    "To fine-tune Transformer-based models (BART and IndicBART) for abstractive summarization.",
    "To support multiple document formats (.txt, .pdf, .docx) and pasted text.",
    "To provide a clean web interface (FastAPI + HTML/CSS/JS) and a Streamlit demo.",
    "To evaluate the fine-tuned models using the ROUGE metric.",
    "To provide an optional Gemini API backend that runs without local models.",
])
section(doc, "1.5", "Scope of the Project")
para(doc, "The project focuses on building a working bilingual summarization tool. Its scope "
     "includes:", after=2)
bullets(doc, [
    "Uploading documents in .txt, .pdf, and .docx formats and extracting their text.",
    "Pasting text directly for summarization.",
    "Generating abstractive summaries in English and Hindi.",
    "Fine-tuning BART on CNN/DailyMail (English) and IndicBART on XL-Sum (Hindi).",
    "Evaluating summarization quality with ROUGE-1, ROUGE-2, ROUGE-L, and ROUGE-Lsum.",
    "A FastAPI web application, a Streamlit demo, and an optional Gemini backend.",
])
para(doc, "The system is designed as an educational and practical demonstration. Summaries of very "
     "long documents are limited by the model's maximum input length.", align="justify")
section(doc, "1.6", "Applications of the Project")
para(doc, "The system can be useful in the following areas:", after=2)
numbered(doc, [
    "Education: Students can summarize long study material, notes, and reports.",
    "News and Media: Readers can obtain quick summaries of long articles in their language.",
    "Government and Administration: Citizens can summarize lengthy notices and reports.",
    "Accessibility: Readers who prefer Hindi can access content in their language.",
    "Research and Business: Professionals can scan reports and documents quickly.",
])

# CHAPTER 2
chapter_title(doc, 2, "Literature Review")
section(doc, "2.1", "Review of Existing Research Papers")
para(doc, "Natural Language Processing, abstractive summarization, and Transformer models are "
     "important research areas related to this project.", align="justify")
subsection(doc, "2.1.1 Attention Is All You Need")
para(doc, "Vaswani et al. (2017) introduced the Transformer architecture, which uses self-attention "
     "to model relationships between elements of a sequence. Transformers are the foundation of "
     "modern sequence-to-sequence models such as BART and IndicBART.", align="justify")
subsection(doc, "2.1.2 BART: Denoising Sequence-to-Sequence Pre-training")
para(doc, "Lewis et al. (2019) introduced BART, a denoising autoencoder that combines bidirectional "
     "and autoregressive Transformers. BART is effective for abstractive summarization and the "
     "bart-large-cnn checkpoint is a standard baseline on CNN/DailyMail.", align="justify")
subsection(doc, "2.1.3 IndicBART for Indian Languages")
para(doc, "Dabre et al. (2022) introduced IndicBART, a pre-trained sequence-to-sequence model for "
     "Indian languages. IndicBART uses a compact mBART-style architecture and a language-token format "
     "that allows fine-tuning for Hindi summarization.", align="justify")
subsection(doc, "2.1.4 XL-Sum: Large-Scale Multilingual Abstractive Summarization")
para(doc, "Hasan et al. (2021) introduced XL-Sum, a multilingual dataset of news article and summary "
     "pairs covering 44 languages, including Hindi. It is used in this project to fine-tune the "
     "Indic model.", align="justify")
table(doc, ["Research / resource", "Main contribution", "Relevance"], [
    ["Vaswani et al. (2017)", "Transformer architecture", "Foundation of BART and IndicBART"],
    ["Lewis et al. (2019)", "BART denoising model", "English abstractive summarizer"],
    ["Dabre et al. (2022)", "IndicBART for Indian languages", "Hindi summarization"],
    ["Hasan et al. (2021)", "XL-Sum multilingual dataset", "Fine-tuning the Hindi model"],
], widths=[4.5, 5.0, 5.5], caption="Table 2.1: Summary of Literature Review")
section(doc, "2.2", "Existing System")
para(doc, "Existing summarization tools mostly target English text. They include cloud-based "
     "summarization APIs, browser extensions, and standalone applications that accept plain text or "
     "web pages.", align="justify")
para(doc, "Indic summarization is less commonly available. Some toolkits support Indian-language NLP "
     "for tasks such as translation and tagging, but integrated document summarization for Hindi is "
     "not readily available to general users.", align="justify")
section(doc, "2.3", "Limitations of Existing System")
numbered(doc, [
    "Most summarization tools support English only.",
    "Regional languages such as Hindi are poorly supported.",
    "Uploading long documents in multiple formats is not always supported.",
    "Many tools require programming knowledge or paid API access.",
])
section(doc, "2.4", "Research Gap")
para(doc, "There is a need for a unified system that accepts documents in multiple formats, supports "
     "both English and Hindi, and provides summaries through a simple web interface. This project "
     "fills that gap by combining fine-tuned BART and IndicBART models with a user-friendly web "
     "front-end.", align="justify")

# CHAPTER 3
chapter_title(doc, 3, "Problem Statement and Requirements")
section(doc, "3.1", "Problem Definition")
para(doc, "The problem addressed by the project is the difficulty readers face in quickly "
     "understanding long documents, especially when the content is in a regional language. A user "
     "requires a simple method to upload a document, choose a language, and receive a short summary "
     "without installing machine-learning libraries.", align="justify")
section(doc, "3.2", "Proposed Solution")
para(doc, "The proposed solution is a bilingual summarization application. The user uploads a "
     "document or pastes text and selects a language. The backend extracts the text and passes it to "
     "the appropriate summarization model. The generated summary is returned to the frontend.",
     align="justify")
para(doc, "The system is implemented using Python and Hugging Face Transformers. Document text is "
     "extracted with PyMuPDF and python-docx, and the web interface is built with FastAPI and a simple "
     "HTML/CSS/JavaScript frontend. A Streamlit version is also provided, and an optional Gemini API "
     "backend is available for lightweight deployment.", align="justify")
section(doc, "3.3", "Functional Requirements")
table(doc, ["ID", "Requirement", "Description"], [
    ["FR01", "Upload document", "Accept .txt, .pdf, and .docx files"],
    ["FR02", "Paste text", "Accept text entered directly in the interface"],
    ["FR03", "Text extraction", "Extract text from the uploaded document"],
    ["FR04", "Language selection", "Allow the user to choose English or Hindi"],
    ["FR05", "Summarize text", "Generate an abstractive summary of the extracted text"],
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
    ["Data privacy", "Uploaded documents should be processed locally"],
], widths=[4.5, 10.5], caption="Table 3.2: Non-Functional Requirements")
section(doc, "3.5", "Hardware and Software Requirements")
table(doc, ["Component", "Requirement"], [
    ["Processor", "Intel Core i5 or equivalent (Apple M-series supported)"],
    ["RAM", "8 GB minimum; 16 GB recommended for model loading"],
    ["Storage", "Approximately 5 GB for models, dependencies, and caches"],
    ["Display", "Standard laptop or desktop display"],
    ["Network", "Internet required for the first model download"],
], widths=[6.0, 9.0], caption="Table 3.3: Hardware Requirements")
table(doc, ["Software", "Purpose"], [
    ["Python 3.10+", "Programming language"],
    ["PyTorch", "Deep-learning backend"],
    ["Hugging Face Transformers", "BART and IndicBART models"],
    ["Hugging Face Datasets", "CNN/DailyMail and XL-Sum loading"],
    ["PyMuPDF / python-docx", "PDF and DOCX text extraction"],
    ["FastAPI + Uvicorn", "Web backend"],
    ["Streamlit", "Demo interface"],
    ["HTML / CSS / JavaScript", "Web frontend"],
    ["Evaluate / rouge_score", "ROUGE evaluation"],
], widths=[6.0, 9.0], caption="Table 3.4: Software Requirements")

# CHAPTER 4
chapter_title(doc, 4, "Proposed Methodology")
section(doc, "4.1", "Overview of the Proposed System")
para(doc, "The system follows a simple client-server architecture. The frontend sends the uploaded "
     "document (or pasted text) and the selected language to the backend. The backend performs text "
     "extraction, selects the appropriate model, generates a summary, and returns it to the "
     "frontend.", align="justify")
numbered(doc, [
    "Frontend: upload interface, language selection, and result display.",
    "Text extraction: PDF, DOCX, and TXT parsing.",
    "Summarization: language-specific BART or IndicBART inference (or the Gemini API).",
    "Training pipeline: fine-tuning scripts and the Kaggle notebooks.",
])
section(doc, "4.2", "System Architecture")
numbered(doc, [
    "Presentation layer: HTML/CSS/JavaScript (FastAPI) and Streamlit.",
    "Extraction layer: PyMuPDF and python-docx.",
    "Model layer: BART (English) and IndicBART (Hindi), loaded from models/ if present.",
    "Optional API layer: Google Gemini, used when SUMMARY_PROVIDER=gemini.",
    "Training layer: Kaggle notebooks and scripts/train.py.",
])
para(doc, "For Hindi, the input is formatted as \u201c<text> </s> <2hi>\u201d and the decoder is "
     "forced to start with the language token, which is required by IndicBART.", align="justify")
section(doc, "4.3", "Workflow of the System")
numbered(doc, [
    "The user opens the web application.",
    "The user uploads a document or pastes text and selects a language.",
    "The backend extracts text using the appropriate extractor.",
    "The text is passed to the language-specific model (or the Gemini API).",
    "The model generates an abstractive summary using beam search.",
    "The summary and extracted text are returned to the frontend.",
    "The user can copy or download the summary.",
])
section(doc, "4.4", "NLP Techniques and Algorithms")
subsection(doc, "4.4.1 Tokenization and Sequence-to-Sequence Modeling")
para(doc, "The input text is tokenized and truncated to the model's maximum input length. The "
     "sequence-to-sequence model generates the summary token by token, conditioned on the encoder "
     "representation of the input.", align="justify")
subsection(doc, "4.4.2 Abstractive Summarization with Beam Search")
para(doc, "Summaries are generated with beam search (num_beams = 4-5), combined with no-repeat "
     "n-gram constraints and length penalties to reduce repetition and control summary length.",
     align="justify")
subsection(doc, "4.4.3 Indic Language Handling")
para(doc, "IndicBART uses a language-token format. The input text is appended with \u201c</s>\u201d and "
     "the language token, the target is prefixed with the language token, and the decoder start token "
     "is set to the language token. This ensures that the generated summary is in the correct script "
     "and language.", align="justify")
subsection(doc, "4.4.4 Optional Gemini Backend")
para(doc, "When the Gemini backend is enabled, the extracted text is sent to the Gemini API with a "
     "language-aware prompt, and the returned summary is displayed. This removes the need for local "
     "model downloads.", align="justify")
section(doc, "4.5", "Dataset Collection and Preprocessing")
bullets(doc, [
    "CNN/DailyMail (English): news articles paired with human-written highlights.",
    "XL-Sum (Hindi): news articles paired with summaries.",
])
para(doc, "XL-Sum is distributed as a script-based dataset, which newer versions of the Datasets "
     "library no longer support. The project therefore loads the auto-converted Parquet shards "
     "directly by URL.", align="justify")
para(doc, "Preprocessing includes tokenization, truncation to the model's maximum length, and, for "
     "IndicBART, language-token formatting. The English data is tokenized normally, while the Hindi "
     "data follows the \u201c<2hi>\u201d format described above.", align="justify")
table(doc, ["Dataset", "Language", "Task", "Usage"], [
    ["CNN/DailyMail", "English", "News summarization", "Fine-tuning BART"],
    ["XL-Sum (hindi)", "Hindi", "News summarization", "Fine-tuning IndicBART"],
], widths=[4.0, 3.0, 4.5, 3.5], caption="Table 4.1: Dataset Description")

# CHAPTER 5
chapter_title(doc, 5, "System Design and Implementation")
section(doc, "5.1", "System Design")
para(doc, "The system is divided into independent modules to simplify development and maintenance.",
     align="justify")
bullets(doc, [
    "Input and upload interface.",
    "Document text extraction (PyMuPDF, python-docx).",
    "Language-aware summarization (BART / IndicBART).",
    "Optional Gemini API backend.",
    "Web API layer (FastAPI).",
    "Frontend (HTML/CSS/JavaScript) and Streamlit demo.",
])
para(doc, "The modules are connected through a shared src/ package so that the web app, the "
     "Streamlit demo, and the training script use the same inference code.", align="justify")
section(doc, "5.2", "Flowchart / UML / DFD Diagrams")
para(doc, "The following diagrams describe the proposed system. They can be inserted into the final "
     "report using draw.io, Microsoft Word Shapes, or another diagram tool.", align="justify")
subsection(doc, "5.2.1 General System Flowchart")
para(doc, "Upload \u2192 text extraction \u2192 language selection \u2192 model inference \u2192 "
     "summary \u2192 display/download.", align="justify")
para(doc, "Figure 5.1: General workflow of the bilingual summarization system.", size=10,
     italic=True, align="center")
subsection(doc, "5.2.2 Data Flow Diagram (Level 0)")
para(doc, "The user provides a document and a language; the system returns a summary. The model and "
     "text-extraction components are internal processes of the application.", align="justify")
para(doc, "Figure 5.2: Level 0 Data Flow Diagram.", size=10, italic=True, align="center")
section(doc, "5.3", "Tools, Technologies and Libraries")
table(doc, ["Technology", "Application"], [
    ["Python", "Core programming language"],
    ["PyTorch", "Deep-learning backend"],
    ["Hugging Face Transformers", "BART and IndicBART models"],
    ["Hugging Face Datasets", "CNN/DailyMail and XL-Sum loading"],
    ["PyMuPDF", "PDF text extraction"],
    ["python-docx", "DOCX text extraction"],
    ["FastAPI + Uvicorn", "Web backend"],
    ["Streamlit", "Demo interface"],
    ["HTML / CSS / JavaScript", "Web frontend"],
    ["Evaluate / rouge_score", "ROUGE evaluation"],
    ["Gemini API (optional)", "Lightweight summarization backend"],
], widths=[6.0, 9.0], caption="Table 5.1: Tools, Technologies and Libraries Used")
section(doc, "5.4", "Implementation Details")
subsection(doc, "5.4.1 Inference Core (src/)")
para(doc, "src/config.py defines the model registry, provider selection, and cache handling. "
     "src/text_extraction.py extracts text from .txt, .pdf, and .docx files. src/summarizer.py loads "
     "the language-specific model and generates the summary, routing to Gemini when configured. "
     "src/llm_api.py implements the Gemini REST client.", align="justify")
subsection(doc, "5.4.2 Web Application")
para(doc, "The FastAPI backend (web/server.py) exposes endpoints for text and document summarization "
     "and serves the static frontend (web/static/), which provides drag-and-drop upload, language and "
     "length controls, and copy/download actions.", align="justify")
subsection(doc, "5.4.3 Streamlit Demo")
para(doc, "app.py provides the same functionality through a simple sidebar-driven Streamlit "
     "interface.", align="justify")
subsection(doc, "5.4.4 Training Pipeline")
para(doc, "The models are fine-tuned using scripts/train.py and the notebooks in notebooks/. Training "
     "uses the Hugging Face Seq2SeqTrainer, and evaluation uses ROUGE-1, ROUGE-2, ROUGE-L, and "
     "ROUGE-Lsum.", align="justify")
section(doc, "5.5", "User Interface and Screenshots")
para(doc, "The web application provides a clean interface for uploading documents and for selecting "
     "the summary language. A screenshot of the running application is shown below.", align="justify")
if SCREENSHOT.exists():
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(SCREENSHOT), width=Cm(15.5))
para(doc, "Figure 5.3: Web Application User Interface", size=10, italic=True, align="center")

# CHAPTER 6
chapter_title(doc, 6, "Results and Discussion")
section(doc, "6.1", "Experimental Setup")
para(doc, "The models were fine-tuned on a Kaggle NVIDIA T4 GPU. BART-base was fine-tuned on "
     "CNN/DailyMail, and IndicBART was fine-tuned on the Hindi subset of XL-Sum. For each language, "
     "2,000 training examples and 200 validation examples were used for two epochs with a batch size "
     "of 4 and a learning rate of 3e-5. Summaries were generated with beam search, and quality was "
     "measured using the ROUGE metric.", align="justify")
section(doc, "6.2", "Test Cases and Sample Outputs")
table(doc, ["Test ID", "Input / Action", "Expected output"], [
    ["TC01", "Open the web application", "Upload interface is displayed"],
    ["TC02", "Upload a valid .txt file", "Text is extracted and shown"],
    ["TC03", "Upload a valid .pdf file", "Text is extracted and shown"],
    ["TC04", "Upload a valid .docx file", "Text is extracted and shown"],
    ["TC05", "Paste text and summarize", "Summary is generated"],
    ["TC06", "Select English and summarize", "English summary is generated"],
    ["TC07", "Select Hindi and summarize", "Hindi summary is generated"],
    ["TC08", "Upload an empty/unsupported file", "A friendly error is shown"],
    ["TC09", "Download the summary", "A .txt file is downloaded"],
], widths=[1.6, 6.4, 7.0], caption="Table 6.1: Functional Test Cases")
section(doc, "6.3", "Performance Evaluation Metrics")
bullets(doc, [
    "ROUGE-1: unigram overlap between the generated and reference summaries.",
    "ROUGE-2: bigram overlap.",
    "ROUGE-L: longest common subsequence.",
    "ROUGE-Lsum: sentence-level longest common subsequence.",
])
section(doc, "6.4", "Results and Observations")
para(doc, "The fine-tuned models produced the following validation results:", after=2)
table(doc, ["Language", "Model", "ROUGE-1", "ROUGE-2", "ROUGE-L", "ROUGE-Lsum"], [
    ["English", "BART-base (CNN/DailyMail)", "40.65", "19.10", "28.30", "37.59"],
    ["Hindi", "IndicBART (XL-Sum)", "60.42", "25.90", "60.36", "60.26"],
], widths=[2.4, 4.6, 1.9, 1.9, 1.9, 2.3], caption="Table 6.2: ROUGE Score Results")
para(doc, "The English model produced concise and relevant summaries. The Hindi model produced "
     "coherent summaries in the Devanagari script. Because only 2,000 examples were used for "
     "fine-tuning, the Hindi model tends to be somewhat verbose and occasionally repeats phrases; "
     "this is expected and can be improved with more training data.", align="justify")
para(doc, "The application was verified end-to-end: documents were uploaded, text was extracted, and "
     "summaries were generated in both languages. Fine-tuned weights placed in models/ are detected "
     "automatically and used instead of the public checkpoints.", align="justify")
section(doc, "6.5", "Limitations")
numbered(doc, [
    "The Hindi model was fine-tuned on a small sample and can be verbose.",
    "Very long documents exceed the model's maximum input length and are truncated.",
    "Summary quality depends on the quality of the extracted text.",
    "The system runs on CPU by default; GPU improves speed.",
    "The local models require a ~2 GB download on first use.",
])

# CHAPTER 7
chapter_title(doc, 7, "Conclusion and Future Scope")
section(doc, "7.1", "Conclusion")
para(doc, "Multilingual Document Summarizer is an NLP-based application that makes long documents "
     "easier to understand in English and Hindi. The project integrates text extraction (PDF, DOCX, "
     "TXT), abstractive summarization using BART and IndicBART, a FastAPI web application, and a "
     "Streamlit demo.", align="justify")
para(doc, "The models were fine-tuned on Kaggle GPUs and evaluated using ROUGE. The English model "
     "achieved a ROUGE-1 of 40.65 and the Hindi model 60.42, showing that the approach is practical. "
     "The project demonstrates how modern NLP and web technologies can be combined to build a useful "
     "bilingual tool.", align="justify")
section(doc, "7.2", "Future Scope")
numbered(doc, [
    "Fine-tune on the full datasets and more epochs for higher-quality summaries.",
    "Add chunking and hierarchical summarization for very long documents.",
    "Support additional Indian languages and scripts.",
    "Improve the Hindi model to reduce repetition and verbosity.",
    "Add voice input and text-to-speech for accessibility.",
    "Deploy the application on a public server with authentication.",
])

# REFERENCES
doc.add_page_break()
para(doc, "REFERENCES", size=14, bold=True, align="center", after=12)
numbered(doc, [
    "Lewis, M., et al. (2019). \u201cBART: Denoising Sequence-to-Sequence Pre-training.\u201d arXiv:1910.13461.",
    "Dabre, R., et al. (2022). \u201cIndicBART: A Pre-trained Model for Natural Language Generation of Indic Languages.\u201d arXiv:2109.02903.",
    "Hasan, T., et al. (2021). \u201cXL-Sum: Large-Scale Multilingual Abstractive Summarization for 44 Languages.\u201d Findings of ACL-IJCNLP 2021.",
    "Vaswani, A., et al. (2017). \u201cAttention Is All You Need.\u201d Advances in Neural Information Processing Systems.",
    "Hermann, K. M., et al. (2015). \u201cTeaching Machines to Read and Comprehend.\u201d NeurIPS. (CNN/DailyMail)",
    "Hugging Face Transformers. https://huggingface.co/docs/transformers/",
    "PyMuPDF Documentation. https://pymupdf.readthedocs.io/",
    "FastAPI Documentation. https://fastapi.tiangolo.com/",
    "Streamlit Documentation. https://docs.streamlit.io/",
    "Google Gemini API. https://ai.google.dev/",
])

# APPENDIX A
doc.add_page_break()
para(doc, "APPENDIX A: IMPORTANT CODE SNIPPETS", size=14, bold=True, align="center", after=12)
para(doc, "Short, relevant excerpts from the project source code are given below.", align="justify")
subsection(doc, "A.1 Summarization Function")
para(doc, "Source file: src/summarizer.py", size=10, italic=True)
para(doc, "The summarize() function loads the language-specific model, tokenizes the input, applies "
     "the IndicBART language format where required, and generates the summary with beam search. It "
     "routes to the Gemini API when SUMMARY_PROVIDER=gemini.", align="justify")
code = ("def summarize(text, language, max_length=None, min_length=None):\n"
        "    if SUMMARY_PROVIDER == \"gemini\":\n"
        "        return summarize_with_gemini(text, language, max_length, min_length)\n"
        "    tokenizer, model = _load_pipeline(language)\n"
        "    inputs = tokenizer(text, max_length=512, truncation=True, return_tensors=\"pt\")\n"
        "    output = model.generate(**inputs, num_beams=4, max_length=128)\n"
        "    return _decode_clean(tokenizer, output[0].tolist())")
p = doc.add_paragraph()
r = p.add_run(code)
r.font.name = "Courier New"
r.font.size = Pt(9)
subsection(doc, "A.2 Text Extraction")
para(doc, "Source file: src/text_extraction.py", size=10, italic=True)
para(doc, "The extract_text() function dispatches to the correct reader based on the file extension.",
     align="justify")
code = ("def extract_text(path):\n"
        "    suffix = Path(path).suffix.lower()\n"
        "    if suffix == \".txt\":  return extract_text_from_txt(path)\n"
        "    if suffix == \".pdf\":  return extract_text_from_pdf(path)\n"
        "    if suffix == \".docx\": return extract_text_from_docx(path)\n"
        "    raise ValueError(f\"Unsupported document type: {suffix}\")")
p = doc.add_paragraph()
r = p.add_run(code)
r.font.name = "Courier New"
r.font.size = Pt(9)
subsection(doc, "A.3 FastAPI Document Endpoint")
para(doc, "Source file: web/server.py", size=10, italic=True)
code = ("@app.post(\"/api/summarize-document\")\n"
        "async def summarize_document(file: UploadFile, language: str = Form(\"en\")):\n"
        "    text = extract_text(file)\n"
        "    summary = summarize(text, language)\n"
        "    return {\"summary\": summary, \"source_text\": text}")
p = doc.add_paragraph()
r = p.add_run(code)
r.font.name = "Courier New"
r.font.size = Pt(9)

# APPENDIX B
doc.add_page_break()
para(doc, "APPENDIX B: ADDITIONAL SCREENSHOTS / OUTPUTS", size=14, bold=True, align="center", after=12)
para(doc, "Sample outputs generated by the system are shown below.", align="justify")
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

doc.save(OUT)
check = Document(OUT)
print("saved:", OUT)
print("paragraphs:", len(check.paragraphs), "tables:", len(check.tables))
