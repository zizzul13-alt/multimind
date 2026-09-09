from types import SimpleNamespace

from providers.groq import GroqProvider
from providers.openrouter import OpenRouterProvider


class FakeCompletions:
    def __init__(self,actual_model): self.actual_model=actual_model; self.calls=[]
    def create(self,**kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="useful answer"))],usage=SimpleNamespace(total_tokens=7),model=self.actual_model)


class FakeChat:
    def __init__(self,actual_model): self.completions=FakeCompletions(actual_model)


class FakeModels:
    def __init__(self,ids): self.ids=ids; self.calls=0
    def list(self):
        self.calls+=1
        return SimpleNamespace(data=[SimpleNamespace(id=item) for item in self.ids])


def test_groq_discovers_then_persists_actual_model(monkeypatch):
    holder={}
    class Client:
        def __init__(self,**_kwargs):
            self.models=FakeModels(["openai/gpt-oss-20b"]); self.chat=FakeChat("openai/gpt-oss-20b"); holder["client"]=self
    monkeypatch.setattr("providers.groq.OpenAI",Client)
    provider=GroqProvider("key")
    first=provider.generate("task",mode="coding")
    second=provider.generate("task 2",mode="research")
    assert first["resolved_model"]=="openai/gpt-oss-20b"
    assert first["actual_model"]=="openai/gpt-oss-20b"
    assert first["model_resolution_source"]=="discovered"
    assert holder["client"].models.calls==1
    assert second["actual_model"]=="openai/gpt-oss-20b"


def test_openrouter_free_router_records_concrete_upstream_model(monkeypatch):
    holder={}
    class Client:
        def __init__(self,**_kwargs): self.chat=FakeChat("provider/live-free-model"); holder["client"]=self
    monkeypatch.setattr("providers.openrouter.OpenAI",Client)
    provider=OpenRouterProvider("key")
    result=provider.generate("task",mode="thinking")
    assert holder["client"].chat.completions.calls[0]["model"]=="openrouter/free"
    assert result["resolved_model"]=="openrouter/free"
    assert result["actual_model"]=="provider/live-free-model"
    assert result["model_resolution_source"]=="provider_dynamic_router"
