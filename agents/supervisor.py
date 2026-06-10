"""
agents/supervisor.py
Agente Supervisor: analiza la intención del usuario y enruta al agente correcto.
Usa AzureChatOpenAI (GPT-4o) via Azure AI Foundry.
"""

from langchain_core.messages import SystemMessage
from langgraph.graph import END

from src.state import MusicAgentState
from src.llm import get_llm


SUPERVISOR_SYSTEM = """Eres el supervisor de un asistente musical especializado.
Tu única tarea es analizar el mensaje del usuario y decidir qué agente especializado
debe responder. NO respondas directamente al usuario.

Los agentes disponibles son:

- **chords_agent**: Para preguntas sobre acordes específicos, progresiones de acordes,
  voicings, inversiones, transposición, y cómo tocar acordes en un instrumento.
  Ejemplos: "dame la progresión ii-V-I en Re", "qué notas tiene un Dm7b5",
  "transponer Am-F-C-G a Bm", "cómo voicear un maj9".

- **theory_agent**: Para preguntas de teoría musical: escalas, modos, armonía funcional,
  contrapunto, géneros musicales (características teóricas), composición, estructura
  de canciones, qué escala usar sobre ciertos acordes, cifrado americano, CAGED, etc.
  Ejemplos: "qué modo es el dorian", "cómo funciona el flamenco armónicamente",
  "diferencia entre armónica menor y melódica", "qué escala usar en jazz modal".

- **search_agent**: Para búsquedas de información en internet: artistas, bandas,
  técnicas de instrumento específicas, equipo/gear, tutoriales, noticias de música,
  discografías, entrevistas, influencias, software DAW, plugins, etc.
  Ejemplos: "información sobre Bill Evans", "técnica de sweep picking",
  "qué guitarra usa John Mayer", "mejores plugins de mezcla 2024".

- **FINISH**: Si el usuario dice adiós, gracias final, o la conversación ha terminado.

Responde SOLO con el nombre del agente (exactamente uno de):
chords_agent | theory_agent | search_agent | FINISH

Sin explicaciones. Solo el nombre."""


def supervisor_node(state: MusicAgentState) -> dict:
    """
    Nodo supervisor: determina qué agente especializado debe responder.
    Temperatura 0 para máxima consistencia en el enrutamiento.
    """
    llm = get_llm(temperature=0)

    messages = [SystemMessage(content=SUPERVISOR_SYSTEM)] + state["messages"]
    response = llm.invoke(messages)

    decision = response.content.strip().lower()

    if "chord" in decision:
        next_agent = "chords_agent"
    elif "theory" in decision:
        next_agent = "theory_agent"
    elif "search" in decision:
        next_agent = "search_agent"
    elif "finish" in decision:
        next_agent = "FINISH"
    else:
        next_agent = "theory_agent"

    return {"next": next_agent}


def route_supervisor(state: MusicAgentState) -> str:
    """
    Función de enrutamiento condicional basada en la decisión del supervisor.
    """
    next_node = state.get("next", "theory_agent")
    if next_node == "FINISH":
        return END
    return next_node
