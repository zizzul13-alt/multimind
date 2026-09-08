from core.compressor import PromptCompressor


class GenericAgent:
    def __init__(self): self.calls=[]
    def generate(self,**kwargs):
        self.calls.append(kwargs)
        # Echoing is intentionally valid but yields no savings; the contract under test
        # is provider-neutral utility invocation plus preservation, not forced shortening.
        original=kwargs["prompt"].split("\n\n",1)[1]
        return {"status":"success","text":original,"tokens":20,"cost":0.0}


def test_compressor_can_use_generic_generate_agent_without_gemini_specific_api():
    agent=GenericAgent(); prompt="MUST preserve config.yaml and 503 while reducing repeated words"
    result=PromptCompressor.compress(prompt,agent)
    assert len(agent.calls)==1
    assert agent.calls[0]["mode"]=="thinking"
    assert result["fallback_reason"] is None
    assert result["compressed"]==prompt
