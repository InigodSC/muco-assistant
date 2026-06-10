"""
src/state.py
Definición del estado compartido entre todos los agentes del grafo.
"""

from typing import Annotated, Literal
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class MusicAgentState(TypedDict):
    """
    Estado compartido entre todos los nodos del grafo multi-agente.

    - messages: historial completo de la conversación (gestionado por add_messages)
    - next: decide a qué agente enrutar (lo establece el Supervisor)
    - current_topic: tema musical activo en la conversación (acordes, escala, etc.)
    """
    messages: Annotated[list, add_messages]
    next: Literal["chords_agent", "theory_agent", "search_agent", "FINISH"]
    current_topic: str
