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

class BMIInput(BaseModel):
    weight: float
    height: float
    weight_unit: str = "kg"
    height_unit: str = "m"

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

@app.post("/calculate-bmi/")
def calculate_bmi(input: BMIInput):
    # Convert weight to kg if not already
    if input.weight_unit == "lb":
        weight_kg = input.weight * 0.453592
    elif input.weight_unit == "kg":
        weight_kg = input.weight
    else:
        return {"error": "Unsupported weight unit. Use 'kg' or 'lb'"}

    # Convert height to meters if not already
    if input.height_unit == "m":
        height_m = input.height
    elif input.height_unit == "in":
        height_m = input.height * 0.0254
    elif input.height_unit == "ft":
        height_m = input.height * 0.3048
    else:
        return {"error": "Unsupported height unit. Use 'm', 'in', or 'ft'"}

    # Calculate BMI
    bmi = weight_kg / (height_m ** 2)

    # Determine BMI category
    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 25:
        category = "Normal weight"
    elif 25 <= bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"

    return {
        "bmi": bmi,
        "category": category,
        "weight_unit": "kg",
        "height_unit": "m"
    }

@app.get("/")
def read_root():
    return {"message": "Welcome to the Health Calculator API"}
