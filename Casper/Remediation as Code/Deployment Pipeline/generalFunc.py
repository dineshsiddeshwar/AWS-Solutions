import aiohttp
import os
import http
import json
from gql import Client
from gql.transport.aiohttp import AIOHTTPTransport
import gqlVariables

# Standard headers
HEADERS_AUTH = {"Content-Type": "application/x-www-form-urlencoded"}
HEADERS = {"Content-Type": "application/json"}

# Environment Variables
client_id = os.getenv("WIZ_CLIENT_ID")
client_secret = os.getenv("WIZ_CLIENT_SECRET")
API_ENDPOINT= "https://api.us4.app.wiz.io/graphql"
WIZ_AUTHENTICATION_URL = "auth.wiz.io"

def query_wiz_api(TOKEN, query: gqlVariables.gqlQueryAndVariable):
# def query_wiz_api(TOKEN, query, variables):
    """Query WIZ API for the given query data schema"""
    HEADERS["Authorization"] = "Bearer " + TOKEN
    transport = AIOHTTPTransport(
        url=API_ENDPOINT,
        headers=HEADERS
    )
    client = Client(transport=transport, fetch_schema_from_transport=True,
                    execute_timeout=55)

    # Fetch the query!
    result = client.execute(query.query, variable_values=query.variables)
    return result
    
def request_wiz_api_token():
    """Retrieve an OAuth access token to be used against Wiz API"""
    headers = {
        "content-type": "application/x-www-form-urlencoded"
    }
    payload = (f"grant_type=client_credentials&client_id={client_id}"
               f"&client_secret={client_secret}&audience=beyond-api")
    conn = http.client.HTTPSConnection(WIZ_AUTHENTICATION_URL)
    conn.request("POST", "/oauth/token", payload, headers)
    res = conn.getresponse()
    if res.status != http.HTTPStatus.OK:
        raise Exception('Error authenticating to Wiz [%d] - %s' %
                        (res.status, res.read()))
    try:
        token_str = res.read().decode("utf-8")
        TOKEN = json.loads(token_str)["access_token"]
        if not TOKEN:
            message = 'Could not retrieve token from Wiz: {}'.format(
                    json.loads(token_str)["message"])
            raise Exception(message)
    except ValueError as exception:
        raise Exception('Could not parse API response: ', exception)
    return TOKEN
    