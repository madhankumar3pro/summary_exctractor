from flask import Flask, render_template, request
from langchain_community.document_loaders import PyPDFLoader
from PyPDF2 import PdfFileReader
# import google.generativeai as genai
# Assuming there is a generativeai module within the google package
import google.generativeai as genai
from io import BytesIO
import fitz
from langchain.text_splitter import TokenTextSplitter


Gemini_pro_API_Key = 'AIzaSyDsWDjM3W_vkZn_lPALwpdWaJSA0aEsh-Y'

genai.configure(api_key=Gemini_pro_API_Key)
gemini_model = genai.GenerativeModel('gemini-pro')

prompt_template = """
Generate a meaningful summary of the following text delimited by triple backquotes.
Return your response in a short and crisp meaningful summary consisting of at least 500.

```{text}```
"""

hyper_parameter = genai.types.GenerationConfig(
    candidate_count=1,
    max_output_tokens=500,
    top_p=0.7,
    top_k=4,
    temperature=0.2
)

app = Flask(__name__)

@app.route('/')
def first_func():
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        try:
            file_content = BytesIO(file.read())
            # pages = PyPDFLoader.load_and_split(file_content)
            pdf_document = fitz.open(stream=file_content.read(), filetype="pdf")
            
            short_pages = ''
            for page_number in range(pdf_document.page_count):
                page = pdf_document[page_number]
                text = page.get_text()
                short_pages = short_pages + ' ' + text
                if len(short_pages.split(' ')) < 28000:
                    text3 = short_pages
                    prompt1 = prompt_template.format(text=text3)
                    response = gemini_model.generate_content(prompt1, generation_config=hyper_parameter)
                    render_template('index.html', result=response.text)
                else:
                    while short_pages:
                        text_splitter = TokenTextSplitter(chunk_size=20000, chunk_overlap=0)
                        texts = text_splitter.split_text(short_pages)
                        final_summary = ''
                        for i in range(1, len(texts)):
                            concatenated_text = texts[i]
                            prompt2 = prompt_template.format(text=concatenated_text)
                            response = gemini_model.generate_content(prompt2, generation_config=hyper_parameter)
                            final_summary = final_summary + ". " + str(response.text.split(' '))

                        if len(final_summary.split(' ')) > 28000:
                            short_pages = final_summary
                            count = count + 1
                            continue
                        else:
                            text2 = final_summary
                            prompt3 = prompt_template.format(text=text2)
                            response = gemini_model.generate_content(prompt3, generation_config=hyper_parameter)
                            break
                return render_template('index.html', result=response.text)
        except Exception as e:
            return render_template('index.html',error_msg = str(e))

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)