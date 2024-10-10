import markdown
# from langchain_google_genai import GoogleGenerativeAI
import google.generativeai as genai
import os

from langchain.prompts import PromptTemplate
from typing import List

class LLM : 
    def __init__(self, **kwargs) -> None:
        self.prompt_file = kwargs.get('prompt_file')
        
        with open(self.prompt_file, 'r') as f:
            self.prompt_template_text = f.read()

        self.prompt_template = PromptTemplate.from_template(self.prompt_template_text)
        self.compare_prompt_path = kwargs.get('compare_prompt_path', None)
        with open(self.compare_prompt_path, 'r') as f:
            self.compare_prompt = f.read()
        self.compare_prompt = PromptTemplate.from_template(self.compare_prompt) if self.compare_prompt is not None else None

        # utils
        self.md = markdown.Markdown()

        self.setup(**kwargs)


    def setup(self, **args) -> None:
        raise NotImplementedError


    def reply(self, prompt : str) -> str:
        raise NotImplementedError


    def get_prompt_template_html(self) -> str:
        '''
        Get the prompt template in HTML format
        '''
        return self.md.convert(self.prompt_template_text)


    def get_prompt_template(self, format='html') -> str:
        '''
        Get the prompt template in the specified format
        '''
        format = format.lower()
        assert format in ['html', 'markdown'], "Invalid format. Must be either 'html' or 'markdown'"
        if format == 'html':
            return self.get_prompt_template_html()
        else:
            return self.prompt_template_text


    def extract_values(self, pdf_text : str, fields : List[str], example_pdf_text : str) -> dict:
        '''
        Extract values from the PDF text
        '''
        prompt = self.prompt_template.format(example_resume=example_pdf_text, resume=pdf_text, fields=fields)
        return self.reply(prompt)

    def compare_values ( self, extracted_values : dict, standard_values : dict ) -> dict:
        '''
        Compare values
        '''
        prompt = self.compare_prompt.format(standard=standard_values, applicant=extracted_values)
        return self.reply(prompt)



    def is_eligible(self, pdf_text : str , standard_values : dict) -> bool:
        pass

class GeminiLLM(LLM):

    def setup(self, **args) -> None:
        
        gemini_api_key = args.get('gemini_api_key', None)
        assert gemini_api_key is not None, "Gemini API key is required"

        with open(gemini_api_key, 'r') as f:
            gemini_api_key = f.read()

        os.environ["GOOGLE_API_KEY"] = gemini_api_key

        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

        self.model_name = args.get('model_name', 'gemini-1.5-flash')
        
        self.llm = genai.GenerativeModel(self.model_name)

    def reply(self, prompt) -> str:
        return self.llm.generate_content(prompt).text

LLMS = {
    'gemini': GeminiLLM
}

if __name__=="__main__":
    llm = GeminiLLM('/home/mahmoud/ATS/src/Templates/prompt1', gemini_api_key='/home/mahmoud/ATS/secrets/gemini_api_key')
    pdf_reader = PDFReader()
    example_pdf = '/home/mahmoud/ATS/Resume Mahmoud Elhusseni - NLP.pdf'

    example_pdf_text = pdf_reader.read_pdf_text(example_pdf)
    fields = ['name', 'email', 'phone', 'experience', 'skills', 'education', 'Social Activities', 'Languages', 'Certifications', 'Projects', 'Hobbies']
    
    
    
    extracted_values = llm.extract_values(example_pdf_text, fields, example_pdf_text)