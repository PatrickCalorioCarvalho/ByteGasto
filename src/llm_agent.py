import json
import re
import os
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_ollama import OllamaLLM


OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://SEU_IP_AQUI:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2:1.5b")


class GastoState(TypedDict):
    transcript: str
    response: str
    gasto: dict


llm = OllamaLLM(
    model=OLLAMA_MODEL,
    base_url=OLLAMA_BASE_URL,
    temperature=0
)

def extract_gasto_node(state: GastoState) -> GastoState:
    prompt = f"""
Você é um extrator de gastos.

Retorne APENAS um JSON válido no formato:
{{
  "Valor": number,
  "Categoria": string
}}

Classifique a categoria do gasto de acordo com estas opções padronizadas: 
- "alimentacao" (ex: mercado, lanche, restaurante, comida, padaria) 
- "bebida" (ex: cerveja, vinho, bar, refrigerante) 
- "transporte" (ex: uber, gasolina, ônibus, metrô, passagem) 
- "moradia" (ex: aluguel, condomínio, luz, água, internet) 
- "lazer" (ex: cinema, show, viagem, festa) 
- "outros" (caso não se encaixe nas anteriores) 


Retorne apenas os campos que existem no texto. 
Não retorne nada além do JSON. 
Não adicione comentários. 
O texto é em português.

Texto: "{state['transcript']}"
"""
    response = llm.invoke(prompt)

    match = re.search(r"\{.*\}", response, re.DOTALL)
    if not match:
        raise ValueError(f"Resposta inválida do LLM: {response}")

    gasto = json.loads(match.group())

    return {
        "transcript": state["transcript"],
        "response": response,
        "gasto": gasto
    }


def _build_graph():
    graph = StateGraph(GastoState)
    graph.add_node("extract", extract_gasto_node)
    graph.set_entry_point("extract")
    graph.add_edge("extract", END)
    return graph.compile()


_graph = _build_graph()


def extract_gasto_data(transcript: str) -> dict:
    result = _graph.invoke({"transcript": transcript})
    return result["gasto"]
