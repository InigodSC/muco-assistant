"""
src/llm.py
Factory centralizada para AzureChatOpenAI.
Todos los agentes llaman get_llm() para obtener el modelo configurado.
"""

import os
from langchain_openai import AzureChatOpenAI


def get_llm(temperature: float = 0.0) -> AzureChatOpenAI:
    """
    Devuelve una instancia de AzureChatOpenAI usando las variables de entorno:
      - AZURE_OPENAI_API_KEY
      - AZURE_OPENAI_ENDPOINT
      - AZURE_OPENAI_API_VERSION
      - AZURE_OPENAI_DEPLOYMENT_NAME

    Args:
        temperature: Temperatura del modelo (0.0 para tareas de enrutamiento,
                     0.2 para respuestas más creativas).
    """
    deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

    return AzureChatOpenAI(
        azure_deployment=deployment,
        api_version=api_version,
        temperature=temperature,
        # azure_endpoint y api_key se leen automáticamente desde:
        # AZURE_OPENAI_ENDPOINT y AZURE_OPENAI_API_KEY
    )
