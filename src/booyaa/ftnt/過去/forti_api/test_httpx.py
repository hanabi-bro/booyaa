from httpx import Client
from urllib.parse import urljoin

session = Client(verify=False, timeout=10.0, follow_redirects=True)
session.headers.update({
    'User-Agent': 'FortiAPI/1.0',
    'Content-Type': 'application/json',
})

def test_httpx():
    try:
        login_data = {
            'username': 'admin',
            'secretkey': 'P@ssw0rd'
        }
        fg_addr = '172.16.201.201'
        url = urljoin('https://', fg_addr, 'logincheck')
        print(f"Attempting to log in to {url} with data: {login_data}")
        response = session.post(urljoin(f'https://{fg_addr}', 'logincheck'), params=login_data)
        response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
        print("Response received successfully:", response._content)
    except Exception as e:
        print(f"An error occurred: {e}")
    response = session.get('https://172.16.201.201/logout')
    if response.status_code == 200:
        print("Logout successful")
    else:
        print(f"Logout failed with status code: {response.status_code}")


if __name__ == "__main__":
    test_httpx()
    session.close()