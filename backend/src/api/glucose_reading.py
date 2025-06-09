# from pydantic import BaseModel

from utils.get_readings import getReadings




# res = gt.get_sgv(start_date = '2024-01-01', end_date = '2024-01-08')


# res['date'] = res['created_at'].dt.date

# average_sgg_by_date = res.groupby('date')['sgv'].mean().round(2).reset_index()
# json_result = average_sgg_by_date.to_json(orient='records', date_format='iso')

# print(json_result)
# print(average_sgg_by_date)


from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter()

class DateRange(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    dates: Optional[List[str]] = None

    aggregation: Optional[str] = None


@router.post("/glucose-readings/")
async def get_glucose_readings(data_range: DateRange):
    gt = getReadings()

    glucose_values = gt.get_sgv(**data_range.dict(exclude_none=True))
    glucose_values['date'] = glucose_values['created_at'].dt.date
    
    if data_range.aggregation == "mean":
        glucose_values = glucose_values.groupby('date')['sgv'].mean().round(2).reset_index()
    
    json_result = glucose_values.to_json(orient='records', date_format='iso')

    return {"data": json_result}
