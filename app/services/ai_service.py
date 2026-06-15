from openai import OpenAI
from app.core.config import OPENAI_API_KEY
from app.services.embedding_service import get_embedding
from app.services.retrieval_service import retrieve_documents
from app.services.escalation_logger import log_escalation

client = OpenAI(api_key=OPENAI_API_KEY)

FALLBACK_MESSAGE = "I couldn't find that information in the apartment documents."

KNOWN_APARTMENTS = [
    "Augustus", "Bafile 18", "Delta", "Delta A", "Delta D",
    "Euroresidence", "Euro 4", "Euro 5", "Ghebo",
    "I Bagni 36", "La Torre", "Torre 1 - 22", "Torre 2 - 21",
    "Lcc6", "Lcc11", "Lcc17", "Lcc2",
    "Maredena", "Maredena A", "Maredena D", "Maredena E", "Maredena F",
    "MariaLuisa", "Piazza Torino",
    "Quito", "Quito 102", "Quito 302",
    "San Silvestro",
    "SunnyHome C2", "SunnyHome C3", "SunnyHome C2 & C3", "SunnyHome C8",
    "Villa", "Villa Alpina 1", "Villa Alpina 2", "Villa Alpina 3",
    "Villa Alpina 4", "Villa Alpina 5", "Villa Alpina 6", "Villa Alpina 7",
    "Villa Dune 1", "Villa Dune 2", "Villa Dune 3", "Villa Dune 4",
    "Villa Dune 5", "Villa Dune 6",
    "Volta", "Volta 1", "Volta 2",
    "Augustus agenzia",
]


TRANSLATIONS = {
    "Italian":  {"dear": "Caro", "dear_guest": "Gentile Ospite", "best_regards": "Cordiali saluti", "team": "Team di Supporto Appartamento (Assistente AI)"},
    "French":   {"dear": "Cher", "dear_guest": "Cher Client", "best_regards": "Cordialement", "team": "Équipe de Support (Assistant IA)"},
    "German":   {"dear": "Lieber", "dear_guest": "Sehr geehrter Gast", "best_regards": "Mit freundlichen Grüßen", "team": "Apartment-Support-Team (KI-Assistent)"},
    "Spanish":  {"dear": "Estimado", "dear_guest": "Estimado Huésped", "best_regards": "Saludos cordiales", "team": "Equipo de Soporte (Asistente IA)"},
    "Portuguese": {"dear": "Caro", "dear_guest": "Caro Hóspede", "best_regards": "Atenciosamente", "team": "Equipe de Suporte (Assistente IA)"},
    "English":  {"dear": "Dear", "dear_guest": "Dear Guest", "best_regards": "Best regards", "team": "Apartment Support Team (AI Assistant)"},
}


def format_email(message: str, guest_name: str = "", language: str = "English") -> str:
    t = TRANSLATIONS.get(language, TRANSLATIONS["English"])
    greeting = f"{t['dear']} {guest_name}," if guest_name else f"{t['dear_guest']},"
    return f"{greeting}\n\n{message}\n\n{t['best_regards']},\n{t['team']}"


def normalize_input(text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Translate the following text to English. If it is already in English, return it unchanged. Return only the translated text, nothing else."
            },
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip()


def detect_intent(text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Classify the following message as either 'question' or 'non_question'. A question is any request, issue, or inquiry. A non_question is a statement, confirmation, or greeting like 'Thanks' or 'I sent deposit'. Return only 'question' or 'non_question'."
            },
            {"role": "user", "content": text}
        ]
    )
    intent = response.choices[0].message.content.strip().lower()
    if intent not in ("question", "non_question"):
        intent = "question"
    return intent


def detect_human_request(text: str) -> bool:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Determine if the guest is explicitly asking to speak with a human, manager, receptionist, "
                    "or any person on the support team. "
                    "Examples that are YES: 'can someone call me', 'I want to talk to a person', "
                    "'speak to a manager', 'human support please', 'is anyone there?'. "
                    "Examples that are NO: regular questions about the apartment, complaints without a request to talk, "
                    "statements, greetings, thanks. "
                    "Return ONLY 'yes' or 'no'."
                )
            },
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip().lower().startswith("y")


def detect_language(text: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Detect the language of the following text. Return ONLY the language name in English (e.g. 'Italian', 'English', 'French', 'German'). Nothing else."
            },
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip()


def extract_guest_name(subject: str, body: str) -> str:
    combined = f"Email subject: {subject}\n\nEmail body: {body}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "Extract the guest's first name from the email. "
                    "Look for patterns like 'Guest name:', 'X said:', or names in the subject line. "
                    "Return ONLY the first name (e.g. 'Yvonne', 'Gabriele'). "
                    "If no guest name can be found, return ONLY the word 'none'."
                )
            },
            {"role": "user", "content": combined}
        ]
    )
    result = response.choices[0].message.content.strip()
    if result.lower() == "none" or len(result) > 30:
        return ""
    return result


def extract_apartment(subject: str, body: str) -> str:
    apartment_list = "\n".join(f"- {a}" for a in KNOWN_APARTMENTS)
    combined = f"Email subject: {subject}\n\nEmail body: {body}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"You are an assistant that identifies which apartment a guest email refers to. "
                f"Below is the list of known apartments:\n{apartment_list}\n\n"
                f"Read the email subject and body carefully. "
                f"If you can identify the apartment, return ONLY the exact apartment name from the list. "
                f"If you cannot identify it, return ONLY the word 'unknown'."
            },
            {"role": "user", "content": combined}
        ]
    )
    result = response.choices[0].message.content.strip()
    if result in KNOWN_APARTMENTS:
        return result
    return ""


def generate_answer(question: str, context: str, language: str = "English") -> str:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an apartment support assistant. "
                    "Answer the guest's question using ONLY the provided context. "
                    "The context may include FAQ entries and apartment manual excerpts. "
                    "Prefer specific, detailed information over general statements. "
                    "Do not use any outside knowledge. Keep the answer helpful and concise. "
                    "Do NOT include any greeting or sign-off — only the answer body. "
                    "The context may contain greetings like 'Buonasera', 'Good morning', 'Dear guest' — ignore them completely and never copy them into your answer. "
                    f"Reply in {language}."
                )
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion:\n{question}"
            }
        ]
    )
    return response.choices[0].message.content.strip()


def handle_non_question(text: str, language: str = "English") -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an apartment support assistant. The guest sent a message that is not a question. "
                    "Respond politely in 1 to 3 sentences. Do not ask questions. Do not provide information. "
                    "Do NOT include any greeting or sign-off — only the response body. "
                    f"Reply in {language}."
                )
            },
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content.strip()


def handle_request(chat_input: str, apartment: str, subject: str = "") -> str:
    language = detect_language(chat_input)
    guest_name = extract_guest_name(subject, chat_input)
    normalized = normalize_input(chat_input)
    intent = detect_intent(normalized)
    human_requested = detect_human_request(normalized)

    if intent == "non_question":
        message = handle_non_question(normalized, language)
        reply = format_email(message, guest_name, language)
        if human_requested:
            log_escalation("human_requested", 0.0, language,
                           apartment, subject, chat_input, reply)
        return reply

    if not apartment:
        apartment = extract_apartment(subject, chat_input)

    if not apartment:
        message = "Could you please provide the name of your apartment? This will help me assist you more accurately."
        reply = format_email(message, guest_name, language)
        if human_requested:
            log_escalation("human_requested", 0.0, language,
                           "", subject, chat_input, reply)
        return reply

    embedding = get_embedding(normalized)
    results, top_similarity = retrieve_documents(embedding, apartment)

    if not results:
        reply = format_email(FALLBACK_MESSAGE, guest_name, language)
        if human_requested:
            log_escalation("human_requested", top_similarity, language,
                           apartment, subject, chat_input, reply)
        return reply

    context = "\n\n---\n\n".join(r["content"] for r in results)
    answer = generate_answer(normalized, context, language)
    reply = format_email(answer, guest_name, language)

    if human_requested:
        log_escalation("human_requested", top_similarity, language,
                       apartment, subject, chat_input, reply)

    return reply
