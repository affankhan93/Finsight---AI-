import json
import os 
import joblib
import pandas as pd 
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import crud, schemas
from backend.auth import get_current_user
from backend.database import get_db
from backend.models import User 

router = APIRouter(prefix='/ml', tags=['ML Inference'])

PREDICT_MODEL_PATH = 'credit_risk_xgb.joblib'
SEGMENT_MODEL_PATH = 'segment_model.joblib'

_loaded_models = {} # cache, so each model is loaded from disk only once

def load_model(path: str):
    if path not in _loaded_models:
        if not os.path.exists(path):
            raise HTTPException(status_code=503, detail=f"Model file not found: {path}")
        _loaded_models[path] = joblib.load(path)
    return _loaded_models[path]

# Supervised learning 
@router.post("/predict", response_model=schemas.PredictResponse)
def predict(req: schemas.PredictRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """predict delinquency riks using the saveed XGBoost model + tuned threshold."""
    bundle = load_model(PREDICT_MODEL_PATH)
    model = bundle['model']
    threshold = bundle['threshold']
    features = bundle['features'] 

    data = {**bundle.get("fill_values", {}), **req.features}

    missing = [f for f in features if f not in data]
    if missing:
        raise HTTPException(status_code=400, detail=f'Missing features: {missing}')
    try:
        df = pd.DataFrame([data])[features]
        probability = float(model.predict_proba(df)[0][1])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {e}")

    prediction = int(probability >= threshold)

    crud.save_log(db, user.id, 'ml/predict', json.dumps(data), f"prediction= {prediction}, probability={probability:.4f}")

    return {'prediction': prediction, 'probability': probability} 


# Unspervised learning
@router.post('/segment', response_model=schemas.SegmentResponse)
def segment(req: schemas.SegmentRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Assign a credit-card customer to a behaviour segment (name + description)."""
    bundle = load_model(SEGMENT_MODEL_PATH)
    model = bundle['model']
    features = bundle['features']
    cluster_config = bundle['cluster_config'] 

    data = {**bundle.get("fill_values", {}), **req.features}

    missing = [f for f in features if f not in data]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing features: {missing}")

    try:
        df = pd.DataFrame([data])[features]
        cluster_id = int(model.predict(df)[0])
    except Exception  as e:
        raise HTTPException(status_code=400, detail=f"Segment failed: {e}") 

    info = cluster_config[cluster_id]

    crud.save_log(db, user.id, 'ml/segment', json.dumps(data), f"cluster={cluster_id}, name={info['name']}")

    return {
        'cluster_id' : cluster_id,
        'name' : info['name'], 
        'description' : info['description'],
        'icon' : info['icon']
    }



