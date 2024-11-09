# Minimal Proxy Server

## Specifications

### Basic Functionality
- Support for the HTTP GET method.
- Ability to forward requests to the appropriate web server based on the requested URL.
- Handle responses from the web server and return them to the client.

### Caching Mechanism
- Implement a simple in-memory cache that stores responses based on URLs.
- Cache entries should include the response content and relevant headers (e.g., Last-Modified).
- Serve cached responses when available, reducing the need for repeated requests to the origin server.

### HTTP Headers
- Handle common HTTP headers such as:
  - **Host**: Determine which server to contact.
  - **If-Modified-Since**: Check if the content has changed before returning cached content.
  - Forward any other headers from the client to the destination server as necessary.

### Error Handling
- Respond with appropriate HTTP status codes for errors:
  - **400 Bad Request**: If the request format is invalid.
  - **404 Not Found**: If the requested resource cannot be found.
  - **405 Method Not Allowed**: If the request method is not supported.
  - **500 Internal Server Error**: If an unexpected condition occurs.

### Logging
- Log requests received, cache hits/misses, and errors for debugging purposes.

## Testing for the Proxy Server

Before testing the proxy server, a simple web server was needed to serve an HTML file (`test.html`). This file simulates a real server that the proxy would forward requests to. Here’s how it was set up using Python's built-in HTTP server:

### Command to Run the Simple HTTP Server
```bash
python -m http.server 8000
