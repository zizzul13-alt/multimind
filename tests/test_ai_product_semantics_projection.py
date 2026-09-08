from multimind_reflex.product_semantics_projection import project_product_semantics


def test_projection_preserves_application_owned_semantics():
    projected=project_product_semantics({"product_semantics":{"mode":"research","prompt_style":"researcher","style_applied":True,"explicit_participants":["gemini","groq"],"capability":{"recommended":["gemini"],"participants":[{"participant_id":"gemini","ready":True}]},"compressor":{"enabled":True,"applied":False,"utility_provider":"groq","fallback_reason":"preservation_guard"}}})
    assert projected["mode"]=="research"
    assert projected["recommended"]==["gemini"]
    assert projected["explicit_participants"]==["gemini","groq"]
    assert projected["compressor_utility_provider"]=="groq"
    assert projected["compressor_fallback_reason"]=="preservation_guard"


def test_projection_malformed_input_fails_boringly():
    projected=project_product_semantics("{broken")
    assert projected["mode"]=="" and projected["recommended"]==[] and projected["explicit_participants"]==[]
