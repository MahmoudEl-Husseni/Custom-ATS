from . import LLMS, PDFReader
class ATS : 
    def __init__(self, cfg : dict) -> None :
        self.cfg = cfg


        self.llm = LLMS.get(cfg['llm']['name'])(**cfg['llm']['args'])
        self.pdf_reader = PDFReader()


    def process(self, file_path : str, key_value_pairs : dict) -> dict:
        '''
        Process the file and key-value pairs
        '''
        pdf_text = self.pdf_reader.read_pdf_text(file_path)
        example_pdf_text = self.pdf_reader.read_pdf_text(self.cfg['example_pdf_path'])
        extracted_values = self.llm.extract_values(pdf_text, key_value_pairs.keys(), example_pdf_text)
        return extracted_values
    
    def compare(self, extracted_values : dict, standard_values : dict) -> dict:
        '''
        Compare extracted values with standard values
        '''
        return self.llm.compare_values(extracted_values, standard_values)