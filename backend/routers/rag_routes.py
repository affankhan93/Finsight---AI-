import os 
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import crud, schemas
from backend.auth import get_current_user
from backend.database import get_db
from backend.models import User
from RAG_pipeline.Retrieval import qa_chain
from RAG_pipeline.Guardrails import check_input, check_output

router = APIRouter(prefix='/rag', tags=['RAG Chat'])

_chain = None 

def get_chain():
    global _chain
    if _chain is None:
        _chain = qa_chain() 
    return _chain

@router.post("/chat", response_model=schemas.ChatResponse)
def chat(req: schemas.ChatRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Ask a question about your documents."""
    # 1. Guardrail on the input (block prompt injection, hides PII)
    ok, clean_question = check_input(req.question)
    if not ok:
        raise HTTPException(status_code=400, detail=clean_question)

    # 2. Run the RAG pipeline (retrieval + reranking + Gro LLM)
    result = get_chain().invoke({"query": clean_question})

    # 3. Guardrail on the output (blocks prompt leaks, hides PII)
    answer = check_output(result['result'])

    # 4. Building a readable list of source 
    sources = []
    for doc in result['source_documents']:
        name = os.path.basename(doc.metadata.get('source', 'unknown'))
        page = doc.metadata.get('page')
        page_text = f"(page {page + 1})" if isinstance(page, int) else "" # page start at 0 
        sources.append(name + page_text)

    # 5. Save a log so the user can rate this answer later 
    log = crud.save_log(db, user.id, 'rag/chat', clean_question, answer)
    return {'answer' : answer, 'sources': sources, 'log_id': log.id}

