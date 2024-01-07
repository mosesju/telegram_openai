from models import SupabaseInteraction

async def query_supabase(supabase, embedding, k, chat_id):
    """Update the supabase database with the latest data."""
    client_res = supabase.rpc("match_documents_personal_profiles", {
            "query_vector": embedding,
            "match_count": k,
            "filter": {"category": chat_id},
        })
    response = client_res.execute()
    if not response or not response.data:
        return None
    else:
        return response


async def update_interaction_supabase(supabase, SupabaseInteraction, table_name):
    """Update the supabase database with the latest data."""
    data = supabase.table(table_name).insert(SupabaseInteraction).execute()
    assert len(data.data) > 0