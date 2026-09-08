from core.application import ChatRequest, MultiMindApplication
from providers.base import BaseProvider

class GenericProvider(BaseProvider):
    def __init__(self,name): super().__init__(name); self.generate_calls=[]
    def generate(self,prompt,system_prompt=None,mode="coding",max_tokens=4096,**kwargs):
        self.generate_calls.append({"prompt":prompt,"system_prompt":system_prompt,"mode":mode,"max_tokens":max_tokens})
        if mode=="thinking" and "Compress the following" in prompt:
            original=prompt.split("\n\n",1)[1]
            return {"status":"success","text":original,"tokens":10,"cost":0.0,"agent":self.name}
        return {"status":"success","text":"direct","tokens":1,"cost":0.0,"agent":self.name}

class Debate:
    def __init__(self,**_kwargs): pass
    def debate(self,**_kwargs): return {"status":"success","final_answer":"ok","responses":[],"participants":[],"total_tokens":0,"total_cost":0.0}

def test_application_uses_generic_selected_provider_as_compression_utility_without_hidden_resource():
    selected=GenericProvider("groq"); hidden=GenericProvider("gemini")
    application=MultiMindApplication(agents={"groq":selected,"gemini":hidden},runtime_memories={},db=object(),debate_factory=Debate)
    result=application.execute_chat(ChatRequest(original_prompt="word "*20,active_agents=["groq"],compressor_enabled=True))
    compressor=result.debate_data["product_semantics"]["compressor"]
    assert compressor["utility_provider"]=="groq"
    assert len(selected.generate_calls)==1
    assert hidden.generate_calls==[]
