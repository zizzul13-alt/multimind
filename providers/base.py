from abc import ABC, abstractmethod

class BaseProvider(ABC):
    """Base class representing an AI service/API Provider."""
    def __init__(self,name:str):
        self.name=name; self.is_available=True; self.last_error=""

    @abstractmethod
    def generate(self,prompt:str,system_prompt:str=None,mode:str="coding",max_tokens:int=4096,**kwargs)->dict:
        pass

    def compress_prompt(self,prompt:str)->dict:
        """Provider-neutral utility capability used only when the caller selects this resource.

        Specialized providers may override this. The base implementation deliberately routes
        through this provider's own generate method and performs no fallback.
        """
        instruction=(
            "Compress the following common task specification to reduce repeated context cost. "
            "Do not add requirements. Preserve every code block, number, filename/path, error/exception, "
            "explicit MUST/DO NOT/NEVER/REQUIRED constraint, and SOURCE/EVIDENCE marker verbatim. "
            "Return only the compressed specification.\n\n"+str(prompt or "")
        )
        response=self.generate(prompt=instruction,system_prompt=None,mode="thinking",max_tokens=4096)
        if not self.has_usable_response(response):
            return {"text":prompt,"original_tokens":0,"compressed_tokens":0,"status":"error"}
        return {"text":response["text"],"original_tokens":0,"compressed_tokens":response.get("tokens",0),"status":"success"}

    def set_availability(self,available:bool,error_msg:str=""):
        self.is_available=available; self.last_error=error_msg

    @staticmethod
    def has_usable_response(response)->bool:
        return isinstance(response,dict) and response.get("status")=="success" and isinstance(response.get("text"),str) and bool(response["text"].strip())

    def failure_response(self,category:str,*,exception_type:str=None,status_code:int=None)->dict:
        result={"status":"error","text":"Provider temporarily unavailable. Trying another provider.","agent":self.model_name if hasattr(self,"model_name") else self.name,"tokens":0,"cost":0.0,"failure_category":category}
        if exception_type: result["exception_type"]=exception_type
        if status_code is not None: result["status_code"]=status_code
        return result
