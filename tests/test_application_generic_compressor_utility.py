from core.application import ChatRequest, MultiMindApplication


class GenericAgent:
    def __init__(self): self.generate_calls=[]
    def generate(self,**kwargs):
        self.generate_calls.append(kwargs)
        if kwargs.get("mode")=="thinking" and "Compress the following" in kwargs.get("prompt",""):
            original=kwargs["prompt"].split("\n\n",1)[1]
            return {"status":"success","text":original,"tokens":10,"cost":0.0}
        return {"status":"success","text":"direct","tokens":1,"cost":0.0}


class Debate:
    def __init__(self,**_kwargs): pass
    def debate(self,**_kwargs): return {"status":"success","final_answer":"ok","responses":[],"participants":[],"total_tokens":0,"total_cost":0.0}


def test_application_uses_generic_selected_agent_as_compression_utility_without_hidden_resource():
    selected=GenericAgent(); hidden=GenericAgent()
    application=MultiMindApplication(agents={"groq":selected,"gemini":hidden},runtime_memories={},db=object(),debate_factory=Debate)
    result=application.execute_chat(ChatRequest(original_prompt="word "*20,active_agents=["groq"],compressor_enabled=True))
    compressor=result.debate_data["product_semantics"]["compressor"]
    assert compressor["utility_provider"]=="groq"
    assert len(selected.generate_calls)==1
    assert hidden.generate_calls==[]
