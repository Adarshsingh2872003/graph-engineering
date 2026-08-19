import os
from pathlib import Path
from pypdf import PdfReader


# =========================================
# RESUME PATH
# =========================================

BASE_DIR = Path(__file__).resolve().parent

RESUME_PATH = BASE_DIR / "my_resume.pdf"


# =========================================
# LOAD RESUME TEXT
# =========================================

def load_resume_text():

    if not RESUME_PATH.exists():

        raise FileNotFoundError(
            f"Resume PDF not found: {RESUME_PATH}"
        )

    print("\n=========================================")
    print("LOADING RESUME")
    print("=========================================")

    print("Resume:", RESUME_PATH)

    reader = PdfReader(str(RESUME_PATH))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text()

        if text:

            pages.append(text)

            print(
                f"Page {page_number}: "
                f"{len(text)} characters"
            )

    resume_text = "\n\n".join(pages)

    if not resume_text.strip():

        raise ValueError(
            "Could not extract text from resume PDF."
        )

    print("\nResume loaded successfully!")

    print(
        "Total characters:",
        len(resume_text)
    )

    return resume_text
if __name__ == "__main__":

    text = load_resume_text()

    print("\n=========================================")
    print("RESUME PREVIEW")
    print("=========================================")

    print(text[:3000])