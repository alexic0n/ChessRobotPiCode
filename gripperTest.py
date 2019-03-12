from util.planner import *
import time

HOST = "192.168.105.110"


def _request(method, endpoint, body=None):
    response = requests.request(method, "http://{}:8000{}".format(HOST, endpoint), json=body)
    # print((method, "http://{}:8000{}".format(HOST, endpoint), body))
    return response.text

_request("POST", "/gripper", body={"move":0})
