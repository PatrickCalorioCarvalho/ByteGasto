import json
import re
from langgraph import Graph, Node
from langgraph.llms import HuggingFaceLLM

def extract_gasto_data(transcript):
    def generate_prompt(transcript):
        return f"""Você é um extrator de gastos. Retorne somente um JSON no formato:
                {{
                "Valor": float,
                "Categoria": str,
                }}
                Classifique a categoria do gasto de acordo com estas opções padronizadas:
                - "alimentacao" (ex: mercado, lanche, restaurante, comida, padaria)
                - "bebida" (ex: cerveja, vinho, bar, refrigerante)
                - "transporte" (ex: uber, gasolina, ônibus, metrô, passagem)
                - "moradia" (ex: aluguel, condomínio, luz, água, internet)
                - "lazer" (ex: cinema, show, viagem, festa)
                - "outros" (caso não se encaixe nas anteriores)
                Retorne apenas os campos que existem no texto no Formato JSON.
                Não retorne nada mais.
                Não adicione comentários.
                O texto é em português.
                Texto: \"{transcript}\" """

    def parse_response(response):
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if not match:
            raise ValueError("Não foi possível extrair o JSON da resposta.")
        return json.loads(match.group(0))

    graph = Graph()
    input_node = Node("Input", lambda x: x)
    prompt_node = Node("Prompt", generate_prompt)
    llm = HuggingFaceLLM(model="google/flan-t5-small") 
    llm_node = Node("LLM", lambda prompt: llm.call(prompt))

    parse_node = Node("Parse", parse_response)
    graph.connect(input_node, prompt_node)
    graph.connect(prompt_node, llm_node)
    graph.connect(llm_node, parse_node)
    result = graph.run(transcript)
    return result