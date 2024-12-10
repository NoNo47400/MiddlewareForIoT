import requests
from enum import Enum
import threading
import time

stop_threads = False  # Indique que le travail est terminé

def handleResponse(r):
    print (r.status_code)
    print (r.headers)
    print (r.text)

class NotificationContentType(Enum):
    ALL_RESOURCE = 1
    MODIFIED_ATTRIBUTES = 2
    RESOURCE_ID = 3

class NotificationEventType(Enum):
    UPDATE_OF_RESOURCE = 1
    DELETE_OF_RESOURCE = 2
    CREATE_OF_DIRECT_CHILD_RESOURCE = 3
    DELETE_OF_DIRECT_CHILD_RESOURCE = 4
    RETRIEVE_OF_CONTAINER_RESOURCE_WITH_NO_CHILD_RESOURCE = 5
    TRIGGER_RECEIVED_FOR_AE_RESOURCE = 6
    BLOCKING_UPDATE = 7


# Faire CIN qui envoie lights-on ou lights-off
# Faire un retrieve pour voir si ils existent deja les containers ou pas
# ajouter des notifications

def createCIN(origin, name, content, path):
    payload = {
        "m2m:cin": {
            "rn": name, 
            "lbl": ["tag:greeting"],
            "cnf": "text/plain:0",
            "con": content
        }
    }
    _headers = {
        'X-M2M-Origin': origin,
        'X-M2M-RI': '123',
        'X-M2M-RVI': '3',
        'Content-Type': 'application/json;ty=4', # contentInstance
    }
    r = requests.post(path, json=payload,headers=_headers)
    handleResponse(r)

def createAE(origin, name, path):
    payload = {
        "m2m:ae": {
            "rn": name, 
            "api": "NnotebookAE", 
            "rr": True, 
            "srv": ["3"]
        }
    }
    _headers = {
        'X-M2M-Origin': origin,
        'X-M2M-RI': '123',
        'X-M2M-RVI': '3',
        'Content-Type': 'application/json;ty=2', # AE
    }
    r = requests.post(path,json=payload,headers=_headers)
    handleResponse(r)

def createCONT(origin, name, path):
    payload = {
        "m2m:cnt": {
            "rn": name
        }
    }
    _headers = {
        'X-M2M-Origin': origin,
        'X-M2M-RI': '123',
        'X-M2M-RVI': '3',
        'Content-Type': 'application/json;ty=3', # Container
    }
    r = requests.post(path,json=payload,headers=_headers)
    handleResponse(r)

def createGroup(origin, name, path, path_container1, path_container2):
    payload = {
        "m2m:grp": {
            "rn": name, # Group Name
            "mid": [
                path_container1, 
                path_container2
            ], 
            "mnm": 10 # maxNrOfMembers
        }
    }
    _headers = {
        'X-M2M-Origin': origin,
        'X-M2M-RI': '123',
        'X-M2M-RVI': '3',
        'Content-Type': 'application/json;ty=9', # group
        'Accept': 'application/json'
    }
    r = requests.post(path,json=payload,headers=_headers)
    handleResponse(r)


def subscribe(origin, name, path, notification_path, notification_content_type, notification_event_type):
    payload = {
        "m2m:sub": {
            "rn": name,
            "nu": notification_path,
            "nct": notification_content_type,
            "enc": {
                "net": notification_event_type
            }
        }
    }
    _headers = {
        "X-M2M-Origin": origin,
        "X-M2M-RI": "123",
        "X-M2M-RVI": "3",
        "Content-Type": "application/json;ty=23", # subscription
        "Accept": "application/json"
    }
    r = requests.post(path,json=payload,headers=_headers)
    handleResponse(r)

def retrieve(origin, path):
    _headers = {
        "X-M2M-Origin": origin,
        "X-M2M-RI": "123",
        "X-M2M-RVI": "3",
        "Accept": "application/json"
    }
    r = requests.get(path,headers=_headers)
    handleResponse(r)
    response_json = r.json()
    return response_json["m2m:cin"]["con"]

def setup_environment():
    createAE("Cmyself_ESP1", "ESP1", 'http://localhost:8080/cse-in')
    createAE("Cmyself_ESP2", "ESP2", 'http://localhost:8080/cse-in')
    createCONT("Cmyself_ESP1", "Led", 'http://localhost:8080/cse-in/ESP1')
    createCONT("Cmyself_ESP2", "Button", 'http://localhost:8080/cse-in/ESP2')
    #createGroup('CAdmin', "Lights-Group", 'http://localhost:8080/cse-in', 'cse-in/AE-BedRoomLights/Light-Container', 'cse-in/AE-KitchenLights/Light-Container')    # Il faut être admin pour créer groupe
    #createCIN("CAdmin", "CIN-LightState", "light-on", 'http://localhost:8080/cse-in/Lights-Group/fopt')
    createCIN("Cmyself_ESP1", "Init", "light-off", 'http://localhost:8080/cse-in/ESP1/Led')
    createCIN("Cmyself_ESP2", "Init", "button-off", 'http://localhost:8080/cse-in/ESP2/Button')
    #subscribe("Cmyself_ESP1", "Subscription", 'http://localhost:8080/cse-in/ESP2/Button', ["http://localhost:9999"], NotificationContentType.ALL_RESOURCE.value, [NotificationEventType.UPDATE_OF_RESOURCE.value])
    

def look_state_button():
    global stop_threads
    while not stop_threads: # Sinon il meurt pas
        state_button = retrieve("Cmyself_ESP2", 'http://localhost:8080/cse-in/ESP2/Button/la')
        if state_button == "button-on":
            createCIN("Cmyself_ESP1", "State"+str(i), "light-on", 'http://localhost:8080/cse-in/ESP1/Led')
        else:
            createCIN("Cmyself_ESP1", "State"+str(i), "light-off", 'http://localhost:8080/cse-in/ESP1/Led')


def change_state_button():
    global stop_threads
    i=0
    while i<10:
        if i%2 == 0:
            createCIN("Cmyself_ESP2", "State"+str(i), "button-off", 'http://localhost:8080/cse-in/ESP2/Button')
        else:
            createCIN("Cmyself_ESP2", "State"+str(i), "button-on", 'http://localhost:8080/cse-in/ESP2/Button')
        i+=1
        time.sleep(2)
    stop_threads = True  

if __name__ == '__main__':
    setup_environment()
    
    thread1 = threading.Thread(target=look_state_button)
    thread2 = threading.Thread(target=change_state_button)
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()

    
