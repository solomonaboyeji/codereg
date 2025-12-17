from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MassInput(BaseModel):
    mass: float
    unit_from: str
    unit_to: str

@app.post("/calculate-mass/")
def calculate_mass(input: MassInput):
    conversion_factors = {
        "g": 1,
        "kg": 1000,
        "mg": 0.001,
        "lb": 453.592,
        "oz": 28.3495
    }

    if input.unit_from not in conversion_factors or input.unit_to not in conversion_factors:
        return {"error": "Invalid unit"}

    mass_in_grams = input.mass * conversion_factors[input.unit_from]
    converted_mass = mass_in_grams / conversion_factors[input.unit_to]

    return {"converted_mass": converted_mass, "unit": input.unit_to}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Mass Calculator API"}
