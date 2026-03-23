def handle_text(text: str) -> str:
    """
    Core logic handler separated from Telegram transport.
    Takes plain text input and routes to the appropriate mock handler.
    """
    text = text.lower().strip()

    if text.startswith("/start"):
        return "Welcome to the LMS Bot! Send me your questions or use /help."
    elif text.startswith("/help"):
        return "Available commands:\n/start - Welcome\n/help - Help listing\n/health - Backend check\n/scores <lab> - Check scores\n/labs - Available labs"
    elif text.startswith("/health"):
        return "Backend is currently healthy and reachable. (Offline test)"
    elif text.startswith("/scores"):
        lab = text.replace("/scores", "").strip() or "general"
        return f"Fetching scores for {lab}... (Not implemented yet)"
    elif text.startswith("/labs"):
        return "Available labs: lab-01, lab-02, lab-03, ... (Not implemented yet)"
    elif "what labs are available" in text:
        return "You can check the available labs by typing /labs (Not implemented yet)"

    # Fallback to LLM / Agent intent routing in later tasks
    return f"You said: {text}. I don't know how to process that yet."
