"""
tools/search_tools.py
Herramienta de búsqueda web en tiempo real con Tavily.
"""

from langchain_core.tools import tool


@tool
def search_music_web(query: str) -> str:
    """
    Busca información musical en internet en tiempo real.
    Útil para: información de artistas, técnicas avanzadas, géneros específicos,
    equipamiento, noticias de música, discografías, entrevistas, tutoriales online.

    Args:
        query: Consulta de búsqueda en cualquier idioma (ej: 'Bill Evans voicing technique',
               'progresión armónica jazz modal', 'Kurt Cobain guitar tuning')

    Returns:
        Resultados de búsqueda web relevantes con fuentes.
    """
    try:
        from tavily import TavilyClient
        import os

        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return "⚠️  TAVILY_API_KEY no configurada. Configura la variable de entorno."

        client = TavilyClient(api_key=api_key)
        # Añadir contexto musical a la búsqueda si no está incluido
        music_query = query if any(w in query.lower() for w in ["music", "guitar", "piano", "chord", "scale", "song", "band", "artist", "musica", "acorde", "escala"]) \
                      else f"{query} music"

        result = client.search(
            query=music_query,
            search_depth="advanced",
            max_results=4,
            include_answer=True,
        )

        output_parts = []

        # Respuesta directa de Tavily si existe
        if result.get("answer"):
            output_parts.append(f"📋 Resumen:\n{result['answer']}\n")

        # Resultados individuales
        for i, r in enumerate(result.get("results", []), 1):
            output_parts.append(
                f"[{i}] {r.get('title', 'Sin título')}\n"
                f"    🔗 {r.get('url', '')}\n"
                f"    {r.get('content', '')[:300]}...\n"
            )

        return "\n".join(output_parts) if output_parts else "No se encontraron resultados."

    except ImportError:
        return "⚠️  Tavily no instalado. Ejecuta: pip install tavily-python"
    except Exception as e:
        return f"❌ Error en búsqueda web: {str(e)}"
