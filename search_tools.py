"""
tools/search_tools.py
Herramienta de búsqueda web en tiempo real con SerpAPI (Google Search).
"""

from langchain_core.tools import tool


@tool
def search_music_web(query: str) -> str:
    """
    Busca información musical en Google en tiempo real usando SerpAPI.
    Útil para: artistas, técnicas, equipo/gear, noticias de música,
    discografías, entrevistas, tutoriales, géneros, historia musical.

    Args:
        query: Consulta de búsqueda (ej: 'Bill Evans voicing technique',
               'mejores pedales de overdrive 2024', 'Kurt Cobain guitar tuning')

    Returns:
        Resultados de búsqueda de Google con snippets y fuentes.
    """
    try:
        from serpapi import GoogleSearch
        import os

        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "⚠️  SERPAPI_API_KEY no configurada. Configura la variable de entorno."

        # Añadir contexto musical si la query no lo tiene
        music_keywords = [
            "music", "guitar", "piano", "chord", "scale", "song", "band",
            "artist", "musica", "acorde", "escala", "jazz", "blues", "rock",
        ]
        if not any(w in query.lower() for w in music_keywords):
            query = f"{query} music"

        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "num": 5,
            "hl": "es",     # resultados preferentemente en español
            "gl": "es",     # región España
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        output_parts = []

        # Answer box (respuesta directa de Google si existe)
        if "answer_box" in results:
            box = results["answer_box"]
            answer = box.get("answer") or box.get("snippet") or box.get("result", "")
            if answer:
                output_parts.append(f"📋 Respuesta directa:\n{answer}\n")

        # Knowledge graph (panel de conocimiento)
        if "knowledge_graph" in results:
            kg = results["knowledge_graph"]
            title = kg.get("title", "")
            desc = kg.get("description", "")
            if title and desc:
                output_parts.append(f"🎵 {title}: {desc}\n")

        # Resultados orgánicos
        organic = results.get("organic_results", [])
        for i, r in enumerate(organic[:4], 1):
            title = r.get("title", "Sin título")
            link = r.get("link", "")
            snippet = r.get("snippet", "")
            output_parts.append(
                f"[{i}] {title}\n"
                f"    🔗 {link}\n"
                f"    {snippet}\n"
            )

        if not output_parts:
            return "No se encontraron resultados para esa búsqueda."

        return "\n".join(output_parts)

    except ImportError:
        return "⚠️  SerpAPI no instalado. Ejecuta: pip install google-search-results"
    except Exception as e:
        return f"❌ Error en búsqueda: {str(e)}"
