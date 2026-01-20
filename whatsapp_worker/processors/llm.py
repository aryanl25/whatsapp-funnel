import logging
from llm.main import chat_with_llm

logger = logging.getLogger(__name__)

def generate_llm_response(user_context: dict, text: str, history: list) -> str:
    try:
        response = chat_with_llm(text, history, user_context=user_context)
        
        if len(response) > 4000:
            logger.error("LLM returned massive payload, likely an error page.")
            return "⚠️ System Error: The AI service returned an invalid response."

        return response

    except Exception as e:
        logger.error(f"LLM Generation failed: {e}", exc_info=True)
        return "⚠️ AI Error: I couldn't process that."
