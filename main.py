# # -*- coding: utf-8 -*-
# """
# This script provides a complete workflow for processing PDF documents:
# 1.  Generates high-quality LaTeX code from a PDF using the Gemini API.
# 2.  Compiles LaTeX code into a PDF file using a local TeX distribution.
# 3.  Converts a PDF file into an editable DOCX file.

# Setup & Dependencies:
# ---------------------
# 1.  Install necessary Python libraries:
#     pip install google-generativeai python-dotenv pdf2docx

# 2.  Set up your Gemini API Key:
#     - Create a file named `.env` in the same directory as this script.
#     - Add the following line to the `.env` file, replacing "YOUR_API_KEY"
#       with your actual key:
#       GEMINI_API_KEY="YOUR_API_KEY"

# 3.  Install a LaTeX Distribution (REQUIRED for latex_to_pdf function):
#     - This script calls the `pdflatex` command-line tool. You must have a
#       LaTeX distribution installed on your system.
#     - For Windows: MiKTeX (https://miktex.org/download)
#     - For macOS: MacTeX (https://www.tug.org/mactex/downloading.html)
#     - For Linux (Debian/Ubuntu): sudo apt-get install texlive-full
# """
# import os
# import subprocess
# import google.generativeai as genai
# from dotenv import load_dotenv
# from pdf2docx import Converter

# # --- Function 1: Generate LaTeX from PDF using Gemini ---

# def get_latex_from_pdf(pdf_file_path: str) -> str:
#     """
#     Analyzes a PDF file using the Gemini Pro Vision model and returns its
#     exact LaTeX code replica.

#     This function uploads the PDF, sends it to the model with a precise
#     prompt, and returns the generated LaTeX code as a string.

#     Args:
#         pdf_file_path (str): The local path to the PDF file.

#     Returns:
#         str: The generated LaTeX code, ready to be compiled.
#              Returns an error message if the API call fails.
#     """
#     print(f"-> Starting LaTeX generation for: {pdf_file_path}")

#     # Load API key from .env file
#     load_dotenv()
#     # api_key = os.getenv("GEMINI_API_KEY")
#     api_key = "AIzaSyDLciV9zoGSvpr2k7_B3xuXa9CotqqmZCE"
#     if not api_key:
#         return "Error: GEMINI_API_KEY not found. Please check your .env file."

#     genai.configure(api_key=api_key)

#     # Prepare the generative model
#     model = genai.GenerativeModel('gemini-2.5-flash')

#     try:
#         # Upload the PDF file to the Gemini API
#         print("   Uploading file to Gemini...")
#         pdf_file = genai.upload_file(path=pdf_file_path)
#         print(f"   File uploaded successfully: {pdf_file.name}")

#         # The prompt is crucial for getting high-quality, error-free LaTeX.
#         # It instructs the model to act as an expert, replicate the layout
#         # exactly, and ensure the code is clean and compilable.
#         prompt = """
#         As a LaTeX expert, your task is to create the exact replica of the
#         provided PDF file in LaTeX.

#         Instructions:
#         1.  Analyze the entire document, including headers, footers, text
#             formatting (bold, italics), tables, lists, and layout.
#         2.  Generate a single, complete, and error-free LaTeX (.tex) code.
#         3.  Ensure the generated code is the best possible version and can be
#             compiled directly without any modifications.
#         4.  Use appropriate packages (like geometry, fancyhdr, tabularx, etc.)
#             to match the original layout perfectly.
#         5.  Do not include any explanations, comments, or conversational text
#             outside of the LaTeX code itself. The output must be only the raw
#             LaTeX code.
#         """

#         # Generate content using the prompt and the uploaded file
#         print("   Sending request to Gemini Pro Vision model...")
#         response = model.generate_content([prompt, pdf_file])
#         print("   Received response from model.")

#         # Clean up the response to ensure it's raw LaTeX code
#         # The model sometimes wraps the code in ```latex ... ```
#         latex_code = response.text
#         print(latex_code)
#         if latex_code.strip().startswith("```latex"):
#             latex_code = latex_code.strip()[7:-3].strip()

#         return latex_code

#     except Exception as e:
#         return f"An error occurred: {e}"

# # --- Function 2: Compile LaTeX to PDF ---

# def compile_latex_to_pdf(latex_code: str, output_filename: str):
#     """
#     Compiles a string of LaTeX code into a PDF file.

#     This function writes the LaTeX code to a .tex file and then uses the
#     `pdflatex` command-line tool to generate a PDF.

#     Args:
#         latex_code (str): The LaTeX code to compile.
#         output_filename (str): The desired name for the output PDF (without extension).
#     """
#     tex_filename = f"{output_filename}.tex"
#     pdf_filename = f"{output_filename}.pdf"
#     log_filename = f"{output_filename}.log"
#     aux_filename = f"{output_filename}.aux"

#     print(f"\n-> Starting LaTeX to PDF compilation...")
#     print(f"   Writing LaTeX code to {tex_filename}")

#     # Write the code to a .tex file
#     with open(tex_filename, "w", encoding="utf-8") as f:
#         f.write(latex_code)

#     # Command to run pdflatex.
#     # -interaction=nonstopmode prevents it from pausing on errors.
#     # -output-directory specifies where to put the generated files.
#     command = [
#         "pdflatex",
#         "-interaction=nonstopmode",
#         "-output-directory=.",
#         tex_filename
#     ]

#     try:
#         print(f"   Running pdflatex command...")
#         # We run it twice to ensure cross-references (like page numbers) are correct.
#         subprocess.run(command, check=True, capture_output=True, text=True)
#         subprocess.run(command, check=True, capture_output=True, text=True)
#         print(f"   Successfully created {pdf_filename}")

#     except FileNotFoundError:
#         print("\n--- ERROR ---")
#         print("'pdflatex' command not found.")
#         print("Please ensure you have a LaTeX distribution (like MiKTeX or TeX Live) installed and in your system's PATH.")
#         print("-------------")
#     except subprocess.CalledProcessError as e:
#         print("\n--- ERROR ---")
#         print(f"LaTeX compilation failed with exit code {e.returncode}.")
#         print("Check the log file for details.")
#         # Write the error log to a file for debugging
#         with open(f"{output_filename}_error.log", "w") as log_file:
#             log_file.write(e.stdout)
#             log_file.write(e.stderr)
#         print(f"Error details saved to {output_filename}_error.log")
#         print("-------------")
#     finally:
#         # Clean up auxiliary files
#         print("   Cleaning up auxiliary files...")
#         for file in [tex_filename, log_filename, aux_filename]:
#             if os.path.exists(file):
#                 os.remove(file)

# # --- Function 3: Convert PDF to DOCX ---

# def convert_pdf_to_docx(pdf_path: str, docx_path: str):
#     """
#     Converts a PDF file to a DOCX file.

#     Args:
#         pdf_path (str): The path to the input PDF file.
#         docx_path (str): The path where the output DOCX file will be saved.
#     """
#     print(f"\n-> Converting {pdf_path} to {docx_path}...")
#     try:
#         # Initialize the converter
#         cv = Converter(pdf_path)
#         # Perform the conversion
#         cv.convert(docx_path, start=0, end=None)
#         cv.close()
#         print(f"   Successfully converted PDF to {docx_path}")
#     except Exception as e:
#         print(f"   An error occurred during PDF to DOCX conversion: {e}")


# # --- Main Execution Block ---

# if __name__ == "__main__":
#     # Define the input PDF file path.
#     # Make sure the PDF file (e.g., "yuvan.pdf") is in the same directory
#     # as this script, or provide the full path to it.
#     source_pdf_path = "yuvan.pdf"

#     if not os.path.exists(source_pdf_path):
#         print(f"Error: The file '{source_pdf_path}' was not found.")
#         print("Please make sure it's in the same directory as the script.")
#     else:
#         # 1. Generate LaTeX code from the source PDF
#         generated_latex = get_latex_from_pdf(source_pdf_path)

#         if "Error:" not in generated_latex:
#             # Save the generated LaTeX code to a file for inspection
#             with open("generated_latex_code.tex", "w", encoding="utf-8") as f:
#                 f.write(generated_latex)
#             print("\n   Generated LaTeX code saved to 'generated_latex_code.tex'")

#             # 2. Compile the generated LaTeX back into a new PDF
#             # This is useful to verify the quality of the generated code.
#             recompiled_pdf_name = "recompiled_from_latex"
#             compile_latex_to_pdf(generated_latex, recompiled_pdf_name)

#             # 3. Convert the original PDF to a DOCX file
#             output_docx_path = "converted_document.docx"
#             convert_pdf_to_docx(recompiled_pdf_name+".pdf", output_docx_path)

#         else:
#             print(f"\nProcess stopped due to an error in LaTeX generation: {generated_latex}")

#     print("\n--- Script finished ---")











































































# main.py
import streamlit as st
import google.generativeai as genai
import os
import subprocess
from pdf2docx import Converter
import tempfile

# --- Page Configuration ---
st.set_page_config(
    page_title="PDF Processor Pro",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="auto",
)

st.title("📄 PDF Processor Pro")
st.markdown("Upload a PDF to convert it into high-quality LaTeX, a recompiled PDF, and an editable DOCX file.")

# --- Helper Functions (Backend Logic) ---

def get_latex_from_pdf(pdf_file_path: str,api=None) -> str:
    """
    Analyzes a PDF file using the Gemini Pro Vision model and returns its
    exact LaTeX code replica.

    This function uploads the PDF, sends it to the model with a precise
    prompt, and returns the generated LaTeX code as a string.

    Args:
        pdf_file_path (str): The local path to the PDF file.

    Returns:
        str: The generated LaTeX code, ready to be compiled.
             Returns an error message if the API call fails.
    """
    print(f"-> Starting LaTeX generation for: {pdf_file_path}")

    # Load API key from .env file
   
    # api_key = os.getenv("GEMINI_API_KEY")
    api_key = "AIzaSyDLciV9zoGSvpr2k7_B3xuXa9CotqqmZCE"
    if not api_key:
        return "Error: GEMINI_API_KEY not found. Please check your .env file."

    genai.configure(api_key=api_key)

    # Prepare the generative model
    model = genai.GenerativeModel('gemini-2.5-flash')

    try:
        # Upload the PDF file to the Gemini API
        print("   Uploading file to Gemini...")
        pdf_file = genai.upload_file(path=pdf_file_path)
        print(f"   File uploaded successfully: {pdf_file.name}")

        # The prompt is crucial for getting high-quality, error-free LaTeX.
        # It instructs the model to act as an expert, replicate the layout
        # exactly, and ensure the code is clean and compilable.
        prompt = """
        As a LaTeX expert, your task is to create the exact replica of the
        provided PDF file in LaTeX.

        Instructions:
        1.  Analyze the entire document, including headers, footers, text
            formatting (bold, italics), tables, lists, and layout.
        2.  Generate a single, complete, and error-free LaTeX (.tex) code.
        3.  Ensure the generated code is the best possible version and can be
            compiled directly without any modifications.
        4.  Use appropriate packages (like geometry, fancyhdr, tabularx, etc.)
            to match the original layout perfectly.
        5.  Do not include any explanations, comments, or conversational text
            outside of the LaTeX code itself. The output must be only the raw
            LaTeX code.
        """

        # Generate content using the prompt and the uploaded file
        print("   Sending request to Gemini Pro Vision model...")
        response = model.generate_content([prompt, pdf_file])
        print("   Received response from model.")

        # Clean up the response to ensure it's raw LaTeX code
        # The model sometimes wraps the code in ```latex ... ```
        latex_code = response.text
        print(latex_code)
        if latex_code.strip().startswith("```latex"):
            latex_code = latex_code.strip()[7:-3].strip()

        return latex_code

    except Exception as e:
        return f"An error occurred: {e}"


def compile_latex_to_pdf(latex_code: str, output_dir: str, base_filename: str) -> str:
    """
    Compiles a string of LaTeX code into a PDF file within a specific directory.
    Optimized for Streamlit with proper error handling and cleanup.

    Args:
        latex_code (str): The LaTeX code to compile.
        output_dir (str): Directory where .tex and .pdf will be stored.
        base_filename (str): The base name for output files (e.g., "my_document").

    Returns:
        str: Path to generated PDF on success, otherwise None.
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    tex_filename = os.path.join(output_dir, f"{base_filename}.tex")
    pdf_filename = os.path.join(output_dir, f"{base_filename}.pdf")

    # Write LaTeX code into .tex file
    with open(tex_filename, "w", encoding="utf-8") as f:
        f.write(latex_code)

    print("hello")
    command = [
        "pdflatex",
        "-interaction=nonstopmode",
        f"-output-directory={output_dir}",
        tex_filename
    ]
    print("hello")
    try:
        # Run twice for references, citations etc.
        for _ in range(2):
            result = os.system(" ".join(command))


        print("hello")
        if os.path.exists(pdf_filename):
            return pdf_filename
        else:
            st.error("LaTeX compilation finished, but no PDF was created. Please check your code.")
            st.code(result.stdout + result.stderr, language="bash")
            return None

    except FileNotFoundError:
        st.error("❌ 'pdflatex' command not found (LaTeX is not installed on this server).")
        st.info("If you're on Streamlit Cloud, add `texlive-xetex` or `texlive-latex-base` to `packages.txt`.")
        return None

    finally:
        # Clean up auxiliary files (but keep .pdf)
        for ext in [".aux", ".log", ".out"]:
            aux_file = os.path.join(output_dir, f"{base_filename}{ext}")
            if os.path.exists(aux_file):
                try:
                    os.remove(aux_file)
                except OSError:
                    pass

def convert_pdf_to_docx(pdf_path: str, output_dir: str, base_filename: str) -> str:
    """Converts a PDF file to a DOCX file."""
    docx_path = os.path.join(output_dir, f"{base_filename}.docx")
    try:
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()
        return docx_path
    except Exception as e:
        st.error(f"Failed to convert PDF to DOCX: {e}")
        return None

# --- Streamlit UI ---

# Get Gemini API Key from user
api_key = st.text_input("🔑 Enter your Gemini API Key", type="password", help="Your key is not stored.")

# File Uploader
uploaded_file = st.file_uploader("📂 Upload your PDF file", type=["pdf"])

if uploaded_file is not None:
    # Get the base filename without extension
    base_filename = os.path.splitext(uploaded_file.name)[0]

    if st.button(f"✨ Process '{uploaded_file.name}'", use_container_width=True):
        if not api_key:
            st.warning("Please enter your Gemini API Key to proceed.")
        else:
            # Create a temporary directory to store all files
            # with tempfile.TemporaryDirectory() as temp_dir:
            if True:
                temp_dir = "new"
                # Save uploaded file to a temporary path
                temp_pdf_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_pdf_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # --- Main Processing Pipeline ---
                st.session_state.latex_code = None
                st.session_state.recompiled_pdf_path = None
                st.session_state.docx_path = None
                
                # Step 1: Generate LaTeX
                with st.spinner("Step 1/3: Generating LaTeX code with Gemini... 🤖"):
                    latex_code = get_latex_from_pdf(temp_pdf_path, api_key)
                    if latex_code:
                        st.session_state.latex_code = latex_code
                        st.success("Step 1/3: LaTeX code generated successfully!")
                    else:
                        st.error("Step 1/3: Failed to generate LaTeX code.")

                # Step 2: Compile LaTeX to PDF
                if st.session_state.latex_code:
                    with st.spinner("Step 2/3: Compiling LaTeX to PDF... 🛠️"):
                        recompiled_pdf_path = compile_latex_to_pdf(st.session_state.latex_code, temp_dir, f"{base_filename}_recompiled")
                        if recompiled_pdf_path and os.path.exists(recompiled_pdf_path):
                            st.session_state.recompiled_pdf_path = recompiled_pdf_path
                            st.success("Step 2/3: PDF compiled successfully!")
                        else:
                            st.error("Step 2/3: Failed to compile PDF.")
                
                # Step 3: Convert original PDF to DOCX
                with st.spinner("Step 3/3: Converting PDF to DOCX... 📝"):
                    docx_path = convert_pdf_to_docx(st.session_state.recompiled_pdf_path, temp_dir, base_filename)
                    if docx_path and os.path.exists(docx_path):
                        st.session_state.docx_path = docx_path
                        st.success("Step 3/3: DOCX converted successfully!")
                    else:
                        st.error("Step 3/3: Failed to convert to DOCX.")
                
                # --- Display Download Buttons ---
                st.markdown("---")
                st.header("📥 Your Files are Ready!")

                col1, col2, col3 = st.columns(3)

                # Download LaTeX (.tex)
                if st.session_state.get('latex_code'):
                    with col1:
                        st.download_button(
                            label="Download LaTeX (.tex)",
                            data=st.session_state.latex_code.encode('utf-8'),
                            file_name=f"{base_filename}.tex",
                            mime="text/plain",
                            use_container_width=True
                        )
                
                # Download Recompiled PDF
                if st.session_state.get('recompiled_pdf_path'):
                    with col2:
                        with open(st.session_state.recompiled_pdf_path, "rb") as pdf_file:
                            st.download_button(
                                label="Download Recompiled PDF",
                                data=pdf_file,
                                file_name=f"{base_filename}_recompiled.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )

                # Download DOCX
                if st.session_state.get('docx_path'):
                    with col3:
                        with open(st.session_state.docx_path, "rb") as docx_file:
                            st.download_button(
                                label="Download DOCX",
                                data=docx_file,
                                file_name=f"{base_filename}.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                use_container_width=True
                            )

