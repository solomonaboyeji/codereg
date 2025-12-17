# Health Calculator API

A FastAPI-based RESTful service for calculating health metrics including mass conversion and BMI calculation.

This project was built by `devstral-small-2:latest`

## Features

- Convert mass between various units (grams, kilograms, milligrams, pounds, ounces)
- Calculate Body Mass Index (BMI) with category classification
- Simple POST endpoints for both mass conversion and BMI calculation
- RESTful API design
- Automatic validation of input data

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd health-calculator
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install fastapi uvicorn pydantic
   ```

## Usage

### Running the API

Start the FastAPI server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### POST /calculate-mass/

Convert mass from one unit to another.

**Request Body:**
```json
{
  "mass": 100,
  "unit_from": "g",
  "unit_to": "kg"
}
```

**Response:**
```json
{
  "converted_mass": 0.1,
  "unit": "kg"
}
```

**Parameters:**
- `mass` (float): The mass value to convert
- `unit_from` (string): Source unit (g, kg, mg, lb, oz)
- `unit_to` (string): Target unit (g, kg, mg, lb, oz)

#### POST /calculate-bmi/

Calculate Body Mass Index (BMI) and get health category.

**Request Body:**
```json
{
  "weight": 70,
  "height": 1.75,
  "weight_unit": "kg",
  "height_unit": "m"
}
```

**Response:**
```json
{
  "bmi": 22.86,
  "category": "Normal weight",
  "weight_unit": "kg",
  "height_unit": "m"
}
```

**Parameters:**
- `weight` (float): Your weight
- `height` (float): Your height
- `weight_unit` (string): Weight unit ('kg' or 'lb')
- `height_unit` (string): Height unit ('m', 'in', or 'ft')

#### GET /

Welcome endpoint that confirms the API is running.

**Response:**
```json
{
  "message": "Welcome to the Health Calculator API"
}
```

## Supported Units

### Mass Conversion
- `g`: grams
- `kg`: kilograms
- `mg`: milligrams
- `lb`: pounds
- `oz`: ounces

### BMI Calculation
- Weight: `kg` (kilograms) or `lb` (pounds)
- Height: `m` (meters), `in` (inches), or `ft` (feet)

## Error Handling

If an invalid unit is provided, the API returns:
```json
{
  "error": "Invalid unit"
}
```

## Testing

You can test the API using curl:

### Test Mass Conversion
```bash
curl -X POST "http://localhost:8000/calculate-mass/" \
  -H "Content-Type: application/json" \
  -d '{"mass": 100, "unit_from": "g", "unit_to": "kg"}'
```

### Test BMI Calculation
```bash
curl -X POST "http://localhost:8000/calculate-bmi/" \
  -H "Content-Type: application/json" \
  -d '{"weight": 70, "height": 1.75, "weight_unit": "kg", "height_unit": "m"}'
```

Or using Python:
```python
import requests

# Test mass conversion
response = requests.post(
    "http://localhost:8000/calculate-mass/",
    json={"mass": 100, "unit_from": "g", "unit_to": "kg"}
)
print(response.json())

# Test BMI calculation
response = requests.post(
    "http://localhost:8000/calculate-bmi/",
    json={"weight": 70, "height": 1.75, "weight_unit": "kg", "height_unit": "m"}
)
print(response.json())
```

You can also run the test script:
```bash
python test_api.py
```

Note: The test script assumes the server is running. Start the server with:
```bash
uvicorn main:app --reload
```

## Project Structure

```
health-calculator/
├── main.py          # FastAPI application
├── README.md        # Project documentation
├── test_api.py      # Test script for API endpoints
├── requirements.txt # Project dependencies
├── pyproject.toml   # Python project configuration
├── venv/            # Virtual environment (created after installation)
└── frontend/        # Frontend application (if any)
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
