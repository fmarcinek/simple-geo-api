# Simple Geo API

**Simple Geo API** is a geolocation service written in **Python 3.12** using the **FastAPI** framework. It integrates with a **PostgreSQL 14** database for data storage and supports both production and testing environments. The API provides functionalities to fetch, store, and delete geolocation data, either from an external IpStack API or directly from app's database.

---

## Technologies Used

- **Programming Language**: Python 3.12
- **Web Framework**: FastAPI
- **Database**: PostgreSQL 14
- **Containerization**: Docker, Docker Compose

---

## Features

- Retrieve geolocation data for IPs and URLs.
- Store geolocation data fetched from an external API or provided directly.
- Delete geolocation data from the database.
- Use Pydantic for data validation and schema generation.
- Full OpenAPI documentation available at `/docs` (Swagger UI) or `/redoc` (ReDoc).

---

## API Endpoints

### 1. **GET /{ip_or_url_value}**
Retrieve geolocation information for a given IP or URL. If there is no demanded record in database or database is unavailable, 
API retreives geolocation data from the external IpStack API (only when `IP_STACK_API_ACCESS_KEY` env variable is set).


**Response**: JSON with geolocation details or a `404 Not Found` if no data is available.

### 2. **POST /geolocation**
Add a geolocation entry to the database. Accepts a JSON body adhering to the Pydantic `IpGeolocationModel` schema.

**Body Example**:
```json
{
    "ip": "192.168.0.1",
    "url": null,
    "continent_code": "NA",
    "continent_name": "North America",
    "country_code": "US",
    "country_name": "United States",
    "region_code": "CA",
    "region_name": "California",
    "city": "San Francisco",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "location": {
        "geoname_id": 123456,
        "capital": "Washington D.C.",
        "country_flag": "https://example.com/flag.png",
        "country_flag_emoji": "🇺🇸",
        "country_flag_emoji_unicode": "U+1F1FA U+1F1F8",
        "calling_code": "1",
        "is_eu": false,
        "languages": [{"code": "en", "name": "English", "native": "English"}],
    },
}
```

### 3. **DELETE /{ip_or_url_value}**
Delete a geolocation entry for a given IP or URL.

**Response**: `204 No Content` if the deletion was successful or `404 Not Found` if no such entry exists.

---

## Data Storage

The database schema consists of the following tables:

1. **IpGeolocation**: Stores geolocation data for IPs and URLs. Geolocation can be stored using only IP value, only URL value or both of them. Both IP and URL values are unique in database.
2. **Location**: Stores location-specific details, including languages and region information.
3. **Language**: Stores languages associated with locations.

### Relationships:
- Each geolocation entry can have one associated location.
- Each location can have multiple languages.

---

## Running the Application

The project uses a `Makefile` for streamlined setup and operations. Below are the available commands:

### Setup and Start

1. **Build and start the application (testing mode):**
   ```bash
   make build-test
   make run-test
   ```

2. **Start the application in production mode:**
   ```bash
   make build
   make run-prod
   ```

3. **Run tests:**
   ```bash
   make test
   ```
   (after building testing application before)

### Database Initialization

- The database is seeded during initialization using scripts located in the `test_db_init_scripts` and `production_db_init_scripts` volumes.
- Custom SQL scripts can be added to these directories for additional setup.

---

## Testing

The project supports automated testing and manual testing via tools like Postman.

### Automated Tests

**Run tests:**
   ```bash
   make test
   ```


### Postman Testing

1. Import the API collection into Postman.
2. Set the base URL to `http://localhost:8000`.
3. Test endpoints with sample data and inspect the responses.

---

## Environment Configuration

The application uses environment variables for configuration. These variables can be set in a `.env` file.

### Example `.env` File:
```env
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
IP_STACK_API_ACCESS_KEY=your_api_key
APP_ENV=development
```

### Docker Compose Integration
Environment variables are loaded into Docker services using the `.env` file.

---

## OpenAPI Documentation

FastAPI provides automatic generation of API documentation. After starting the application, you can access the documentation at:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Error Handling

The application implements custom error handling to return meaningful HTTP status codes:

- `404 Not Found`: Geolocation entry not found.
- `500 Internal Server Error`: Database or external API errors.
- `400 Bad Request`: Validation errors for provided data.
- `422 Unprocessable Entity`: Validation errors for provided json data.
