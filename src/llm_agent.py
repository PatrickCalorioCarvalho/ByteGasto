import json
import re
import ollama

def extract_gasto_data(transcript):
    prompt = f"""Você é um extrator de gastos. Retorne somente um JSON no formato:
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
    
    completion = ollama.chat(
        model="phi3",
        messages=[{"role": "user", "content": prompt}]
    )["message"]["content"]
   
    match = re.search(r'\{.*\}', completion, re.DOTALL)
    if not match:
        raise ValueError("Não foi possível extrair o JSON da resposta.")
    
    data = json.loads(match.group(0))
    return data