# from pydantic import BaseModel, Extra, Field
# from typing import Optional, List, Dict, Any
# from datetime import date

# class DateParams(BaseModel):
#     start_date: Optional[date] = None
#     end_date: Optional[date] = None
#     dates: Optional[List[date]] = None

#     class Config:
#         extra = 'allow'

# def test(**kwargs):
#     params = DateParams(**kwargs)
#     print(params)


# test(start_date = '2024-13-12')

from utils.get_readings import getReadings

gt = getReadings()

# res = gt._build_date_query('test', start_date = '2023-12-12')
# res = gt.get_bolus_wizard(start_date = '2023-12-12')
# print(res)

res = gt.get_bolus_wizard(dates = ['2024-01-01', '2023-12-12'])
print(res)