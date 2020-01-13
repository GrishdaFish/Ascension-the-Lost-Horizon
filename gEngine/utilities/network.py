# importing the requests library
import requests
import json

# TODO CONSIDER how stateless?  how will we generate/hide api key?
class NetworkController():
    def __init__(self):
        # api-endpoint
        self.API_URL = "https://criticalmiss-studios.com/network/network.php"

    def send_package(self, request_type, data):
        # TEST CALLS ## COMMENT OR REMOVE THIS BLOCK ###############
        request_type = "add_player"
        data = {'user_name': "user02", 'user_pass': "12345"}
        ############################################################


        # defining a params dict for the parameters to be sent to the API
        req_params = {'request': request_type,
                      'api_key': "12345",
                      'data': json.dumps(data)}
        # send get request and save the response as response object
        r = requests.post(url=self.API_URL, data=req_params)

        # extracting data in json format  ### currently not passing it back this way (YET)
        # data = r.json()

        ########### TODO DEBUGGING SECTION:  REMOVE ALL THIS SHIT #######################################
        # printing the response code 200=ok 300=redirect 400=fnf 500=bork
        print("%s" % r)
        # printing response content, this is the data you will want to work with
        print("TEXT: %s" % r.text)

        # prints all variables of the response object for debugging
        from pprint import pprint
        pprint(vars(r))
        #################################################################################################



nc = NetworkController()
nc.send_package(0,0)