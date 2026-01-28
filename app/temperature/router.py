import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.city.crud import get_all_cities
from app.temperature import crud, schemas
from app.services.temperature_updater import fetch_and_create_temperature


router = APIRouter()


@router.post("/temperatures/update/", response_model=list[schemas.TemperatureRead])
async def update_temperatures(db: Session = Depends(get_db)):
    cities = get_all_cities(db=db)

    if not cities:
        raise HTTPException(status_code=404, detail="No cities in database.")

    new_temperatures = await asyncio.gather(
        *(fetch_and_create_temperature(db, city) for city in cities)
    )

    return new_temperatures


@router.get("/temperatures/", response_model=list[schemas.TemperatureRead])
def get_all_temperatures(db: Session = Depends(get_db)):
    temperatures = crud.get_all_temperatures(db=db)
    return temperatures


@router.get("/temperatures/{city_id}/", response_model=list[schemas.TemperatureRead])
def get_temperatures_by_city(city_id: int, db: Session = Depends(get_db)):
    temperatures = crud.get_temperatures_by_city(db=db, city_id=city_id)

    if not temperatures:
        raise HTTPException(status_code=404, detail=f"No temperatures found for city_id={city_id}")

    return temperatures
