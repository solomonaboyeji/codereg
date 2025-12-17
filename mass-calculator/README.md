# Mass Calculator API

A FastAPI-based RESTful service for converting mass between different units.

This project was built by `devstral-small-2:latest`

## Features

- Convert mass between various units (grams, kilograms, milligrams, pounds, ounces)
- Simple POST endpoint for mass conversion
- RESTful API design
- Automatic validation of input data

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd mass-calculator
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

#### GET /

Welcome endpoint that confirms the API is running.

**Response:**
```json
{
  "message": "Welcome to the Mass Calculator API"
}
```

## Supported Units

- `g`: grams
- `kg`: kilograms
- `mg`: milligrams
- `lb`: pounds
- `oz`: ounces

## Error Handling

If an invalid unit is provided, the API returns:
```json
{
  "error": "Invalid unit"
}
```

## Testing

You can test the API using curl:
```bash
curl -X POST "http://localhost:8000/calculate-mass/" \
  -H "Content-Type: application/json" \
  -d '{"mass": 100, "unit_from": "g", "unit_to": "kg"}'
```

Or using Python:
```python
import requests

response = requests.post(
    "http://localhost:8000/calculate-mass/",
    json={"mass": 100, "unit_from": "g", "unit_to": "kg"}
)
print(response.json())
```

## Project Structure

```
mass-calculator/
├── main.py          # FastAPI application
├── README.md        # Project documentation
└── venv/            # Virtual environment (created after installation)
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
