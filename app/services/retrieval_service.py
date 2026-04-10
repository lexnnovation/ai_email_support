from app.db.supabase_client import supabase


def retrieve_documents(query_embedding, apartment, match_count=5):
    response = supabase.rpc(
        "match_documents",
        {
            "query_embedding": query_embedding,
            "match_count": match_count,
            "apartment_filter": apartment
        }
    ).execute()

    results = response.data or []

    apt_lower = apartment.lower()
    apartment_docs = [
        r for r in results if apt_lower in r.get("content", "").lower()]
    general_docs = [r for r in results if r not in apartment_docs]

    return apartment_docs + general_docs
