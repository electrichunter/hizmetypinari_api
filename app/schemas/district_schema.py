from pydantic import BaseModel

class DistrictBase(BaseModel):
    name: str
    city_name: str

class DistrictCreate(DistrictBase):
    pass

class District(DistrictBase):
    id: int

    class Config:
        from_attributes = True
