# 🎵 Music Composer Assistant

Agente multi-agente construido con **LangGraph** y tracing en **LangSmith**.

## Arquitectura

```
Usuario
  │
  ▼
┌─────────────────────┐
│   Supervisor Agent  │  ← Enruta la intención del usuario
└──────┬──────────────┘
       │
   ┌───┴────────────────────────────────┐
   │            │              │        │
   ▼            ▼              ▼        ▼
Chords       Theory        Search    Memory
Agent        Agent         Agent     Store
(acordes,   (teoría,      (web,    (historial
 progres.)   escalas)      noticias) sesión)
```

### Agentes especializados

| Agente | Función |
|--------|---------|
| **Supervisor** | Analiza la intención y enruta al agente correcto |
| **Chords Agent** | Acordes, progresiones, voicings, transposición |
| **Theory Agent** | Escalas, modos, armonía, contrapunto, géneros |
| **Search Agent** | Búsqueda web en tiempo real (artistas, noticias, técnicas) |

### Features
- ✅ Multi-agente con Supervisor que enruta dinámicamente
- ✅ Memoria persistente por sesión (thread_id) con `MemorySaver`
- ✅ Tracing automático en LangSmith
- ✅ Búsqueda web en tiempo real (Tavily)
- ✅ Historial de conversación para contexto musical continuo

## Setup

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Variables de entorno
```bash
cp .env.example .env
# Edita .env con tus API keys
```

### 3. Ejecutar
```bash
python main.py
```

## Ejemplo de uso

```
🎵 Pregunta: dame una progresión de jazz en Dm
🎵 Pregunta: qué escala usaría sobre esa progresión?
🎵 Pregunta: busca información sobre Bill Evans y su estilo de voicings
🎵 Pregunta: cómo funciona el rearm en blues?
```

## Variables de entorno necesarias

| Variable | Descripción |
|----------|-------------|
| `LANGSMITH_API_KEY` | API key de LangSmith |
| `LANGSMITH_TRACING` | `true` para activar tracing |
| `LANGSMITH_PROJECT` | Nombre del proyecto en LangSmith |
| `ANTHROPIC_API_KEY` | API key de Anthropic (Claude) |
| `TAVILY_API_KEY` | API key de Tavily (búsqueda web) |
