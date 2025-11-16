# core/context_processors.py
def participant(request):
    return {"participant_id": request.session.get("participant_id")}