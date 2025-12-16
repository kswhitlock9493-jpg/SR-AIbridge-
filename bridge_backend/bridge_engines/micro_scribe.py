from pydantic import BaseModel
class DiffAnalysis(BaseModel): lines:int=0
class PRTemplate(BaseModel): title:str=""; body:str=""
class SovereignMicroScribe:
    def analyse(self, payload:dict)->DiffAnalysis: return DiffAnalysis()
    def template(self)->PRTemplate: return PRTemplate()
