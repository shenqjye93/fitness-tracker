from fastapi import APIRouter
from pydantic import BaseModel

import json

router = APIRouter()

class Metric(BaseModel):
    id: int
    category: str = "metrics"
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


@router.get("/health-metrics")
async def get_health_metrics():
    return read_data()
     

@router.post("/health-metrics/{metric_id}")
async def create_metric(metric_id: str, metric: Metric):
    data = read_data()
    data[metric_id] = metric.dict()
    write_data(data)
    return data[metric_id]
