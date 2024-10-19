# Face Encoding

## Introduction

This project enables customers to utilize Veriff’s Face Encoding product, which provides a streamlined process for face verification and recognition. The workflow consists of four main steps:

**Session Creation**: The customer initiates a session with Veriff by providing relevant verification data (e.g., callback URL, vendor data). A unique session ID is generated for tracking the entire process.

**Image Upload**: The customer uploads image files (up to 5 faces per image) as part of the verification process. Each image is linked to the session.

**Face Encoding Creation**: Veriff processes the uploaded images to generate face encodings for every detected face. These encodings are used for identity verification and recognition.

**Session Summary**: After processing all images, Veriff generates a session summary that includes all face encodings from the uploaded images. This summary is returned to the customer, providing valuable biometric data for further analysis or verification.

### API Endpoints
Create Session: Start a new session by providing verification data.
Upload Media: Upload images to an existing session.
Get Decision: Retrieve the face encoding results and session summary.

## Developing

The project comes with a set of commands you can use to run common operations for your stack:

- `make install`: Installs run time dependencies.
- `make install-dev`: Installs dev dependencies together with run time dependencies.
- `make lint`: Runs static analysis.
- `make coverage`: Runs all tests collecting coverage.
- `make test`: Runs `lint` and `component`.

### Running the service locally in Docker

To build and run the python service as well as a Statsd container:

```bash
docker-compose build
docker-compose up
```

The service should now be available on http://127.0.0.1:8000/docs

### Running the service outside of Docker

This is useful if you want to debug the service through an IDE or just run it from console.

Firstly it is useful to create a virtual environment to run a version of python and isolate a projects dependencies.
Change the face encoding url (face_encoding_service_url) to http://localhost:8000/v1/selfie
Create a virtual environment in the root of your project: 

Linux/Mac:

```bash
pyvenv venv
source venv/bin/activate
```

Install the project dependencies into it:

```bash
make install
```

To run the Python service use:

```bash
make run
```

To run the Unit tests use:

```bash
make unit
```

## Services

Here are the curl commands for the provided APIs. 
Port (8000) in running outside docker or 8001 within docker
## 1. Create Session (POST /api/sessions)
```bash
curl -X 'POST' \
  'http://127.0,0,1:8001/api/sessions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "verification": {
      "callback": "http://example.com/callback",
      "vendorData": "1e1d09a8-4674-41df-b2f3-25c3bd5efd58",
      "document": {
        "number": "AB123456",
        "country": "US",
        "type": "SELFIE"
      }
    }
  }'
```
## 2. Upload Media (POST /api/sessions/{sessionId}/media)
```bash
curl -X 'POST' \
  'http://127.0.0.1:8001/api/sessions/{sessionId}/media' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "image": {
      "context": "selfie",
      "content": "iVBORw0KGgoAAAANSUhEUgAAAAUA...",  # Base64-encoded image
      "image_type": "png/jpg/bmp"
    }
  }'
Replace {sessionId} with the actual session ID in the URL.
```
## 3. Get Decision (GET /api/sessions/{session_id}/decision)
```bash
curl -X 'GET' \
  'http://127.0.0.1:8001/api/sessions/{session_id}/decision' \
  -H 'accept: application/json'

Replace {session_id} with the actual session ID in the URL.
```


## Contributing
Check the CONTRIBUTING.md files