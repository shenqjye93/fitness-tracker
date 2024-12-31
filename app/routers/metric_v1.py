from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pathlib import Path
from typing import List

import json

router = APIRouter()

class Readings(BaseModel):
    systolic: int
    diasystolic: int
    pulse: int

class BP(BaseModel):
    id: int
    category: str = "metric"
    type: str
    level: Readings

class Glucose(BaseModel):
    id: int
    category: str = "metric"
    type: str
    level: int

data_file = "data/data.json"

def read_data():
    try:
        with open(data_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    
## call function to write/ update data
def write_data(data):
    with open(data_file, "w") as f:
        json.dump(data, f, indent=4)

@router.get("/metrics")
async def get_metric():
    return read_data()

@router.get("/get-metrics/{metrics_id}")
async def get_metric(metrics_id: str):
    metrics = read_data()
    if metrics_id not in metrics:
        raise HTTPException(status_code=404, detail="Error, metric not found")
    
    metric = metrics[metrics_id]
    
    if metric["category"] == "metric":
        return metric
    else:
        raise HTTPException(status_code=404, detail="Error, metric not found")
    

@router.post("/create-bp/{metrics_id}")
async def create_metric(metrics_id: str, metric: BP):
    metrics = read_data()
    if metrics_id in metrics:
        return {"message": "Metric Exists"}
    ## updates metrics data with new info
    metrics[metrics_id] = metric.dict() #metric model is not dict
    write_data(metrics)
    return metrics[metrics_id] 


@router.put("/create-bp/{metrics_id}")
async def update_metric(metrics_id: str, metric: BP):
    metrics = read_data()
    if metrics_id not in metrics:
        raise HTTPException (status_code=404, detail= "Error, metric not found")
    metrics[metrics_id] = metric.dict() 
    write_data(metrics)
    return metrics[metrics_id] 


@router.post("/create-glucose/{metrics_id}")
async def create_metric(metrics_id: str, metric: Glucose):
    metrics = read_data()
    if metrics_id in metrics:
        return {"message": "Metric Exists"}
    ## updates metrics data with new info
    metrics[metrics_id] = metric.dict() #metric model is not dict
    write_data(metrics)
    return metrics[metrics_id] 


@router.put("/create-glucose/{metrics_id}")
async def update_metric(metrics_id: str, metric: Glucose):
    metrics = read_data()
    if metrics_id not in metrics:
        raise HTTPException (status_code=404, detail= "Error, metric not found")
    metrics[metrics_id] = metric.dict() 
    write_data(metrics)
    return metrics[metrics_id] 

@router.delete("/delete-metrics/{metrics_id}")
async def delete_metric(metrics_id: str):
    metrics = read_data()
    if metrics_id not in metrics:
        raise HTTPException (status_code=404, detail= "Error, metric not found")
    else:
        del metrics[metrics_id]
        write_data(metrics)
        return {"detail": f"metric {metrics_id} has been deleted"}

