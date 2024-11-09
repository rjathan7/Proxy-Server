import requests

def test_proxy():
    print("Basic GET:")
    response = requests.get("http://localhost:8080/test.html")
    print(response.status_code, response.text)
    print("=" * 40)

    print("If-Modified-Since is before modified time:")
    response = requests.get("http://localhost:8080/test.html", headers={"If-Modified-Since": "Sat, 20 Oct 2024 19:26:00 GMT"})
    print(response.status_code, response.text)
    print("=" * 40)

    print("If-Modified-Since is after modified time:")
    response = requests.get("http://localhost:8080/test.html", headers={"If-Modified-Since": "Tue, 22 Oct 2024 19:26:00 GMT"})
    print(response.status_code, response.text)
    print("=" * 40)

    print("Bad Request:")
    response = requests.post("http://localhost:8080/test.html", data={"some": "value"})
    print(response.status_code, response.text)
    print("=" * 40)

    print("Not Found:")
    response = requests.get("http://localhost:8080/non_existent_test.html")
    print(response.status_code, response.text)
    print("=" * 40)

if __name__ == "__main__":
    test_proxy()
