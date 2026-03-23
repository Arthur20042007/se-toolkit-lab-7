from services.backend import backend_client

async def handle_text(text: str) -> str:
    """
    Core logic handler separated from Telegram transport.
    Takes plain text input and routes to the appropriate handler.
    """
    text = text.lower().strip()

    if text.startswith("/start"):
        return "Welcome to the LMS Bot! Send me your questions or use /help."
    elif text.startswith("/help"):
        return (
            "Available commands:\n"
            "/start - Welcome message with bot name\n"
            "/help - Lists all commands with descriptions\n"
            "/health - Reports healthy/unhealthy status\n"
            "/labs - Lists labs available\n"
            "/scores <lab> - Check per-task scores for a lab"
        )
    elif text.startswith("/health"):
        try:
            items = await backend_client.get_items()
            count = len(items) if items else 0
            return f"Backend is healthy. {count} items available."
        except Exception as e:
            return str(e)
    elif text.startswith("/scores"):
        parts = text.split()
        if len(parts) < 2:
            return "Please provide a lab identifier, e.g. /scores lab-04"
        lab = parts[1]
        try:
            scores = await backend_client.get_scores(lab)
            if not scores:
                return f"No pass rates found for {lab}."
            lines = [f"Pass rates for {lab.capitalize().replace('-', ' ')}:"]
            for score in scores:
                task_name = score.get("task", "Unknown")
                avg = score.get("avg_score", 0.0)
                attempts = score.get("attempts", 0)
                lines.append(f"- {task_name}: {avg}% ({attempts} attempts)")
            return "\n".join(lines)
        except Exception as e:
            return str(e)
    elif text.startswith("/labs"):
        try:
            items = await backend_client.get_items()
            # Filter and format labs
            labs = [item for item in items if item.get("type", "") == "lab"]
            if not labs:
                return "No labs available at the moment."
            
            lines = ["Available labs:"]
            for lab in labs:
                lines.append(f"- {lab.get('title')}")
            return "\n".join(lines)
        except Exception as e:
            return str(e)
    elif "what labs are available" in text:
        return await handle_text("/labs")

    if text.startswith("/"):
        return "Unknown command. Use /help to see available commands."
    
    # Fallback to LLM / Agent intent routing in later tasks
    return f"You said: {text}. I don't know how to process that yet."
