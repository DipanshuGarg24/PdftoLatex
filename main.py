
# main.py
import streamlit as st
import google.generativeai as genai
import os
from pdf2docx import Converter
import tempfile
import shutil
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
st.markdown("Built by Dipanshu Garg")
# --- Helper Functions (Backend Logic) ---

def get_latex_from_pdf(pdf_file_path: str,api_key=None) -> str:
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
    # with open("new.tex" , "r") as f:
    #     return f.read()
   
    # api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        return "Error: GEMINI_API_KEY not found. Please check your .env file."

    genai.configure(api_key=api_key)

    # Prepare the generative model
    model = genai.GenerativeModel('gemini-2.5-pro')

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
        st.code(latex_code)
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
if "latex_code" not in st.session_state:
    st.session_state.latex_code = None

if "recompiled_pdf_path" not in st.session_state:
    st.session_state.recompiled_pdf_path = None

if "docx_path" not in st.session_state:
    st.session_state.docx_path = None

if 'down' not in st.session_state:
    st.session_state.down = False

if 'Temp_dir' not in st.session_state:
    st.session_state.Temp_dir = None

# Get Gemini API Key from user
# api_key = st.text_input("🔑 Enter your Gemini API Key", type="password", help="Your key is not stored.")

# File Uploader
uploaded_file = st.file_uploader("📂 Upload your PDF file", type=["pdf"])


if uploaded_file is not None:
    # Get the base filename without extension
    base_filename = os.path.splitext(uploaded_file.name)[0]
    
    if st.session_state.down:
        if st.button("Reset :)",type="primary"):
            # // reset thing
            st.session_state.down = False
            st.session_state.latex_code = None
            if st.session_state.Temp_dir and os.path.exists(st.session_state.Temp_dir):
                shutil.rmtree(st.session_state.Temp_dir)
            st.rerun()
        else:
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



    elif st.button(f"✨ Process '{uploaded_file.name}'", use_container_width=True):
        # if not api_key:
        #     st.warning("Please enter your Gemini API Key to proceed.")
        # else:
        if True:
            # Create a temporary directory to store all files
        # 2. Create a new persistent temporary directory
            st.session_state.Temp_dir = tempfile.mkdtemp()
            temp_dir = st.session_state.Temp_dir
            if temp_dir:
                # Save uploaded file to a temporary path
                temp_pdf_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_pdf_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # --- Main Processing Pipeline ---
                
                
                # Step 1: Generate LaTeX
                with st.spinner("Step 1/3: Generating LaTeX code with Gemini... 🤖"):
                    latex_code = get_latex_from_pdf(temp_pdf_path,st.secrets["api_key"])
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
                        st.session_state.down = True
                        st.rerun()
                    else:
                        st.error("Step 3/3: Failed to convert to DOCX.")
                
                



