import requests
def handleResponse(r):
    print (r.status_code)
    print (r.headers)
    print (r.text)

def createCIN():
    payload = {
        "m2m:cin": {
            "cnf": "text/plain:0",
            "con": "Noel is here!"
        }
    }
    _headers = {
        'X-M2M-Origin': 'Cmyself',
        'X-M2M-RI': '123',
        'X-M2M-RVI': '3',
        'Content-Type': 'application/json;ty=4', # contentInstance
    }
    r = requests.post('http://localhost:8080/cse-in/Notebook-AE/Container',json=payload,headers=_headers)
    handleResponse(r)

if __name__ == '__main__':
    createCIN()