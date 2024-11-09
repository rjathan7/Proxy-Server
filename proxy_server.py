from socket import *
import os
import datetime 

# cache to store responses and their last modified time
CACHE = {}  # key: URL, value: (content, last_modified_time)

def handle_client_request(client_socket):
    # receive the http request from the client
    request = client_socket.recv(1024).decode()
    print("Recieved request:\n", request)

    # split request into lines and extract first line
    lines = request.splitlines()
    first_line = lines[0].split()  # ex) ['GET', '/test.html', 'HTTP/1.1']

    # check if request format is valid (contains at least 3 parts)
    if len(first_line) < 3:
        client_socket.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\n")
        client_socket.close()  # close connection
        return
    
    # extract method (GET), URL, HTTP from first line
    method, url, http_version = first_line[0], first_line[1], first_line[2]

    if method.upper() != 'GET':
        client_socket.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
        client_socket.close()
        return
    
    # separate host from the headers
    host = None
    for line in lines:
        if line.lower().startswith("host:"):
            host = line.split(':', 1)[1].strip()  # extract host
            break

    if not host:
        client_socket.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\n")
        client_socket.close()  # close connection
        return

    # if the request is for the proxy itself, we should extract the real target host
    if "localhost:8080" in host:
        # using "localhost" as the host and default HTTP port
        host = "localhost"  # the server is assumed to be running on localhost
        port = 8000  
    else:
        port = 80  # default port for other hosts

    # check if the URL is absolute or relative
    if url.startswith("http://"):
        url_parts = url.split('/')
        host = url_parts[2]  # domain ex) example.com
        path = '/' + '/'.join(url_parts[3:])
    else:
        # if it's a relative URL, construct the full URL
        path = url  # just the path
        url = f"http://{host}{path}"  # construct the full URL

    if url in CACHE:
        cached_content, last_modified = CACHE[url]
        print("Cache hit for: ", url)

        # prepare response with cached content
        response = f"HTTP/1.1 200 OK\r\nLast-Modified: {last_modified}\r\nContent-Length: {len(cached_content)}\r\nContent-Type: text/html\r\n\r\n"
        response = response.encode() + cached_content  # combine headers and content
        client_socket.sendall(response)  # send cached response to client
    else:
        print("Cache miss, forwarding request to origin server")

        # create new socket connection to origin server
        origin_socket = socket(AF_INET, SOCK_STREAM)
        try:
            origin_socket.connect((host, port))  # connect to origin server
        except Exception as e:
            print(f"Failed to connect to {host}:{port} - {e}")
            client_socket.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
            client_socket.close()
            return

        # forward request to origin server
        origin_socket.sendall(request.encode())

        # prepare to receive the response from the origin server
        origin_response = b""  # initialize empty byte string 

        # read response in chunks until no more data is received
        while True:
            chunk = origin_socket.recv(4096)  # receive up to 4096 bytes
            if not chunk:
                break  # exit loop if there's no more data
            origin_response += chunk  # append received chunk to response

        origin_socket.close()  # close connection to origin server

        # check if origin server returned a valid response (HTTP 200 OK)
        if origin_response.startswith(b"HTTP/1.1 200 OK"):
            # Extract last modified time from response headers
            headers = origin_response.split(b'\r\n')  # split response into headers
            content = origin_response.split(b'\r\n\r\n', 1)[1]  # get response body (content)
            last_modified = None  # initialize last modified time

            # loop through headers to find the 'Last-Modified' header
            for header in headers:
                if header.lower().startswith(b'last-modified:'):
                    last_modified = header.split(b': ', 1)[1].decode()  # get the value of Last-Modified header

            # cache new response and its last modified time in cache
            if last_modified:
                CACHE[url] = (content, last_modified)

            # prepare the response to send back to the client
            response = f"HTTP/1.1 200 OK\r\nLast-Modified: {last_modified}\r\nContent-Length: {len(content)}\r\nContent-Type: text/html\r\n\r\n"
            response = response.encode() + content  # Combine headers and content
            client_socket.sendall(response)  # Send the response back to the client

        elif origin_response.startswith(b"HTTP/1.1 304 Not Modified"):
            # if the response is 304, serve the cached content
            cached_content, last_modified = CACHE[url]  # retrieve cached content

            response = f"HTTP/1.1 200 OK\r\nLast-Modified: {last_modified}\r\nContent-Length: {len(cached_content)}\r\nContent-Type: text/html\r\n\r\n"
            response = response.encode() + cached_content  # combine headers and cached content
            client_socket.sendall(response)  # send the cached response to the client

        else:
            # for any other responses (e.g., errors), send the original response back to the client
            client_socket.sendall(origin_response)

    client_socket.close()  # close the connection to the client

def run_proxy_server():
    server_port = 8080  # define port for the proxy server
    proxy_socket = socket(AF_INET, SOCK_STREAM)  # create a new socket for the proxy server
    proxy_socket.bind(("0.0.0.0", server_port))  # bind the socket to all interfaces on the specified port
    proxy_socket.listen(5)  # listen for up to 5 connections
    print(f"Proxy server listening on port {server_port}")  # log that the server is running
    
    # loop to accept incoming connections
    while True:
        client_socket, addr = proxy_socket.accept()  # accept new connection from a client
        print("Accepted connection from", addr)  # log client's address
        
        handle_client_request(client_socket)  # handle the client's request

if __name__ == "__main__":
    run_proxy_server()  # run the proxy server when the script is executed
