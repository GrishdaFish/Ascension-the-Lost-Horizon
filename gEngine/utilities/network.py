# importing the requests library
import requests
import json

# TODO CONSIDER how stateless?
class NetworkController():
    def __init__(self):
        # api-endpoint, this will most likely change before release
        self.API_URL = "https://criticalmiss-studios.com/network/network.php"
        # store the most recent response
        self.current_response = None

    def send_package(self, request_type, data):
        """  Prepares and sends a package to the game server, returns a dictionary
        :param request_type: string telling the server wtf u want
        :param data: dictionary to be processed by the server ( use only double quotes on key names! *see below )
        :return: dictionary: { "message": 'msg from server or fail msg', "data": {"requested_data" : value, ...} }
        """
        # TEST CALLS ## COMMENT OR REMOVE THIS BLOCK ###############
        # request_type = "add_player"
        # data = {'user_name': "user02", 'user_pass': "12345"}
        ############################################################

        # defining a params dict for the parameters to be sent to the API
        req_params = {'request': request_type,
                      'api_key': "12345",  ## TODO how will we generate/hide api key?
                      'data': json.dumps(data)}
        # send get request and save the response as response object
        self.current_response = requests.post(url=self.API_URL, data=req_params)
        # extracting data from json to python dict
        # data = json.loads(self.current_response.text)
        data = self.get_response_content()

        # TODO DEBUGGING SECTION:  REMOVE ALL THIS SHIT ####################################
        # printing the response code 200=ok 300=redirect 400=fnf 500=bork
        # print("%s" % self.current_response)
        # printing response content, this is the data you will want to work with
        # print("TEXT: %s" % self.current_response.text)

        # prints all variables of the response object for debugging
        from pprint import pprint
        pprint(vars(self.current_response))
        # TODO###############################################################################

        if str(self.current_response.status_code) == "200":
            return data
        else:
            return {"message": "Failed to connect to server. Please check connection and try again."}

    def get_response_content(self):
        """ Returns complete server package
            { "message": 'msg from server or fail msg', "data": {"requested_data" : value, ...} } """
        return json.loads(self.current_response.text)

    def get_response_data(self):
        """ Returns only the data portion of the package """
        return self.current_response.json()['data']

    def get_response_msg(self):
        """ Returns only the message portion of the package"""
        return self.current_response.json()['message']
