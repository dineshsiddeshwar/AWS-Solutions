from time import sleep
import requests
import socket 
import boto3
from botocore.exceptions import ClientError
import base64
import json
import datetime as dt
from datetime import datetime
from datetime import timedelta
import json
import jwt
import cryptography
import cffi
import time
import urllib.request
from zipfile import ZipFile
import os
import random

class DNSDelegation(object):
    """
    # AWS@Shell Public DNS Delegation
    """
    def __init__(self, event, context):
        self.event = event
        self.context = context
        try:
            session_client = boto3.Session()
            self.ssm_client = session_client.client('ssm' ,region_name="us-east-1")

            self.sns_topic_arn = 'arn:aws:sns:us-east-1:' + event['detail']['recipientAccountId'] + ':platform_Compliance_Security_Notification'
            self.sns_client = session_client.client('sns', region_name="us-east-1")
            
            self.accountNumber = event['detail']['recipientAccountId']
            print("Account number identified is:", self.accountNumber)

            platform_Custodian_dl = self.ssm_client.get_parameter(Name='/Platform-Tag/platform_Custodian')
            self.platform_Custodian_dl = platform_Custodian_dl['Parameter']['Value']
            print("platform Custodian dl", self.platform_Custodian_dl)

            platform_dl = self.ssm_client.get_parameter(Name='/Platform-Tag/platform_DL')
            self.platform_dl = platform_dl['Parameter']['Value']
            print("platform dl", self.platform_dl)

            gridmaster = self.ssm_client.get_parameter(Name='/platform-dns/gridmasterapigee')
            ## Dev - "api-dev.shell.com/ds"
            self.gridmasteragigee = gridmaster['Parameter']['Value']
            print("gridmaster APIGEE name is", self.gridmasteragigee)

            gridmasterExtnl = self.ssm_client.get_parameter(Name='/platform-dns/gridmasterapigee')
            ## gridmaster external
            self.gridmasteragigeeExtnl = gridmasterExtnl['Parameter']['Value']
            print("gridmaster Extnl APIGEE name is", self.gridmasteragigeeExtnl)

            appid = self.ssm_client.get_parameter(Name='/platform-dns/github-appid')
            ## github app id
            self.github_app_id = appid['Parameter']['Value']
            print("gGit Hub App ID is ", self.github_app_id)
            
            workflowid = self.ssm_client.get_parameter(Name='/platform-dns/github-workflowid')
            ## github workflow file name
            self.github_workflow_id = workflowid['Parameter']['Value']
            print("github workflow file name is", self.github_workflow_id)
            
            secretarn = self.ssm_client.get_parameter(Name='/platform-dns/secretarn')
            ## github secret arn name
            self.secretarn = secretarn['Parameter']['Value']
            
            template = self.ssm_client.get_parameter(Name='/platform-dns/templateid')
            ## github secret arn name
            self.templateid = template['Parameter']['Value']
            print("github template id is", self.templateid)
            
            owner = self.ssm_client.get_parameter(Name='/platform-dns/ownername')
            ## github secret arn name
            self.owner_name = owner['Parameter']['Value']
            print("github template id is", self.owner_name)
            
            repo = self.ssm_client.get_parameter(Name='/platform-dns/reponame')
            ## github secret arn name
            self.repo_name = repo['Parameter']['Value']
            print("github template id is", self.repo_name)
            
            job_step = self.ssm_client.get_parameter(Name='/platform-dns/job_step_name')
            ## github secret arn name
            self.job_and_steps_path = job_step['Parameter']['Value']
            print("github Job name and step name that is 3rd step name:- ", self.job_and_steps_path)
            
            gmapiversion = self.ssm_client.get_parameter(Name='/platform-dns/gmapiversion')
            ## GM API Version till today is - "v2.11.2"
            self.gmapiversion = gmapiversion['Parameter']['Value']
            print("gm api version is", self.gmapiversion)

            gmapiversionExtnl = self.ssm_client.get_parameter(Name='/platform-dns/gmapiversion')
            ## GM Extnl API Version till today is - "v2.11.2"
            self.gmapiversionExtnl = gmapiversionExtnl['Parameter']['Value']
            print("gm Extnl api version is", self.gmapiversionExtnl)

            APIGEEAuthorizationTokenExtnl = self.ssm_client.get_parameter(Name='/platform-dns/APIGEEAuthorizationTokenExtnl')
            ## APIGEE Extnl Authorization Token
            self.APIGEEAuthorizationTokenExtnl = APIGEEAuthorizationTokenExtnl['Parameter']['Value']
            print("APIGEE Extnl Authorization Token is", self.APIGEEAuthorizationTokenExtnl)

            APIGEEAuthorizationToken = self.ssm_client.get_parameter(Name='/platform-dns/APIGEEAuthorizationToken')
            ## APIGEE Authorization Token
            self.APIGEEAuthorizationToken = APIGEEAuthorizationToken['Parameter']['Value']
            print("APIGEE Authorization Token is", self.APIGEEAuthorizationToken)

            ADOAuthorizationToken = self.ssm_client.get_parameter(Name='/platform-dns/ADOAuthorizationToken')
            ## ADO Authorization Token
            self.ADOAuthorizationToken = ADOAuthorizationToken['Parameter']['Value']
            print("ADO Authorization Token is", self.ADOAuthorizationToken)

            APIGEEAuthorizationURL = self.ssm_client.get_parameter(Name='/platform-dns/APIGEEAuthorizationURL')
            ## APIGEE Authorization URL
            self.APIGEEAuthorizationURL = APIGEEAuthorizationURL['Parameter']['Value']
            print("APIGEE Authorization URL is", self.APIGEEAuthorizationURL)

            APIGEEAuthorizationURLExtnl = self.ssm_client.get_parameter(Name='/platform-dns/APIGEEAuthorizationURL')
            ## APIGEE Extnl Authorization URL
            self.APIGEEAuthorizationURLExtnl = APIGEEAuthorizationURLExtnl['Parameter']['Value']
            print("APIGEE Extnl Authorization URL is", self.APIGEEAuthorizationURLExtnl)

            ADOAPIURL = self.ssm_client.get_parameter(Name='/platform-dns/ADOAPIURL')
            ## ADO API URL
            self.ADOAPIURL = ADOAPIURL['Parameter']['Value']
            print("APIGEE Authorization URL is", self.ADOAPIURL)

            ADOReleaseId = self.ssm_client.get_parameter(Name='/platform-dns/ADOReleaseId')
            ## ADO Release Id API URL
            self.ADOReleaseId = ADOReleaseId['Parameter']['Value']
            print("ADO Release Id is", self.ADOReleaseId)

            DNSSESKeyEmail = self.ssm_client.get_parameter(Name='/platform-dns/DNSSESKeyEmail')
            ## Email for infoblox team
            self.DNSSESKeyEmail = DNSSESKeyEmail['Parameter']['Value']
            print("DNS SES Key Email", self.DNSSESKeyEmail)

            DNSSESSecrtEmail = self.ssm_client.get_parameter(Name='/platform-dns/DNSSESSecrtEmail')
            ## Email for infoblox team
            self.DNSSESSecrtEmail = DNSSESSecrtEmail['Parameter']['Value']
            print("DNS SES Secrt Email", self.DNSSESSecrtEmail)
        except Exception as exception:
            raise Exception(str(exception))

    def IPAddressNSlookUp (self, fqdn):
        try :
            socket_info = socket.gethostbyname(fqdn)
            print("socket info returned is", socket_info)
            if socket_info :
                print ("IP Returned after nslookup is", socket_info)
                return socket_info
            else:
                return False
        except Exception as exception:
                print(str(exception))
                return False

    def IPAddressNSlookUpExtnl (self, fqdn):
        try :
            socket_info = socket.gethostbyname(fqdn)
            print("Extnl socket info returned is", socket_info)
            if socket_info :
                print ("Extnl IP Returned after nslookup is", socket_info)
                return socket_info
            else:
                return False
        except Exception as exception:
                print(str(exception))
                return False

    def GetAPIGEEBearerToken (self):
        try: 
            print("In Get APIGEE Bearer Token......")
            if self.APIGEEAuthorizationURL and self.APIGEEAuthorizationToken :
                print("APIGEE Authorization URL and Token is retrived to get bearer token..")
                headers = {'Content-Type': 'application/x-www-form-urlencoded','Authorization': 'Basic '+self.APIGEEAuthorizationToken}
                payload='grant_type=client_credentials'
                GetAPIGEEBearerTokeresponse = requests.request("POST", self.APIGEEAuthorizationURL, headers=headers, data=payload)
                if  GetAPIGEEBearerTokeresponse.status_code == 200:
                    print("retrieved the bearer token..")
                    print(json.loads(GetAPIGEEBearerTokeresponse.text)['access_token'])
                    return json.loads(GetAPIGEEBearerTokeresponse.text)['access_token']
                else:
                    print("Did not get the required response , hence sending error emails to Ops")
                    return False
            else:
                print("APIGEE Authorization URL and Token not retrieved, hence sending error emails to Ops exits now..")
                return False
        except Exception as exception:
            print(str(exception))
            print("exception occured hence.. returns false")
            return False

    def GetAPIGEEBearerTokenExtnl (self):
        try: 
            print("In Get APIGEE Bearer Token Extnl......")
            if self.APIGEEAuthorizationURLExtnl and self.APIGEEAuthorizationTokenExtnl :
                print("APIGEE Authorization URL and Token is retrived to get bearer token Extnl..")
                headers = {'Content-Type': 'application/x-www-form-urlencoded','Authorization': 'Basic '+self.APIGEEAuthorizationTokenExtnl}
                payload='grant_type=client_credentials'
                GetAPIGEEBearerTokeresponse = requests.request("POST", self.APIGEEAuthorizationURLExtnl, headers=headers, data=payload)
                if  GetAPIGEEBearerTokeresponse.status_code == 200:
                    print("retrieved the bearer token Extnl..")
                    print(json.loads(GetAPIGEEBearerTokeresponse.text)['access_token'])
                    return json.loads(GetAPIGEEBearerTokeresponse.text)['access_token']
                else:
                    print("Did not get the required response Get APIGEE bearer token Extnl , hence sending error emails to Ops")
                    return False
            else:
                print("APIGEE Authorization URL and Token for Extnl not retrieved, hence sending error emails to Ops exits now..")
                return False
        except Exception as exception:
            print(str(exception))
            print("exception occured hence.. returns false")
            return False

    def CheckIfParentZoneExists (self , event):
        try: 
            print("In check if Parent zone exists......")
            print(event['detail']['responseElements'])
            responseElements = event['detail']['responseElements']
            hostedzonename = responseElements['hostedZone']['name'][:-1]
            print("Hosted zone found is : ", hostedzonename)
            todelegatezone = hostedzonename.split('.', 1)[0]
            print("to delegate zone is", todelegatezone)
            parentzone = hostedzonename.split('.', 1)[1]
            print("parent zone is", parentzone)
            apigee_bearer_token = self.GetAPIGEEBearerToken()
            if apigee_bearer_token :
                print("APIGEE bearer token is retrieved..")
                checkzoneurl = 'https://'+self.gridmasteragigee+'/wapi/'+self.gmapiversion+'/zone_auth?fqdn~=^'+parentzone+'$&_return_fields=fqdn&_return_as_object=1' ## GET
                headers = {'Authorization': 'Bearer '+apigee_bearer_token}
                payload={}
                PZresponse = requests.request("GET", checkzoneurl, headers=headers, data=payload)
                PZresponseResult = json.loads(PZresponse.text)
                print(PZresponseResult)
                if  PZresponse.status_code == 200 and len(PZresponseResult['result']) != 0:
                    print("retrieved the response..hence parent domain exists..")
                    print(json.loads(PZresponse.text))
                    return json.loads(PZresponse.text)
                else:
                    print("Did not get the required response check parent zone , hence sending false")
                    return False
            else:
                print("Did not retrieve the APIGEE bearer token at check parent zone, hence exits now..")
                return False
        except Exception as exception:
            print(str(exception))
            print("exception occured at check parent zone hence.. returns false")
            return False

    def CheckIfParentZoneExistsExtnl (self , event):
        try: 
            print("In check if Parent zone exists Extnl......")
            print(event['detail']['responseElements'])
            responseElements = event['detail']['responseElements']
            hostedzonename = responseElements['hostedZone']['name'][:-1]
            print("Hosted zone found is : ", hostedzonename)
            todelegatezone = hostedzonename.split('.', 1)[0]
            print("to delegate zone is", todelegatezone)
            parentzone = hostedzonename.split('.', 1)[1]
            print("parent zone is", parentzone)
            apigee_bearer_token = self.GetAPIGEEBearerTokenExtnl()
            if apigee_bearer_token :
                print("APIGEE bearer token is retrieved Extnl..")
                checkzoneurl = 'https://'+self.gridmasteragigeeExtnl+'/wapi/'+self.gmapiversionExtnl+'/zone_auth?fqdn~=^'+parentzone+'$&_return_fields=fqdn&_return_as_object=1' ## GET
                headers = {'Authorization': 'Bearer '+apigee_bearer_token}
                payload={}
                PZresponse = requests.request("GET", checkzoneurl, headers=headers, data=payload)
                PZresponseResult = json.loads(PZresponse.text)
                print(PZresponseResult)
                if  PZresponse.status_code == 200 and len(PZresponseResult['result']) != 0:
                    print("retrieved the response..hence parent domain exists Extnl..")
                    return json.loads(PZresponse.text)
                else:
                    print("Did not get the required response check parent zone , hence sending false")
                    return False
            else:
                print("Did not retrieve the APIGEE bearer token at check parent zone, hence exits now..")
                return False
        except Exception as exception:
            print(str(exception))
            print("exception occured at check parent zone hence.. returns false")
            return False

    def CheckIfSubZoneExists (self , event):
        try:
            print("In check if SubZone exists for create......")
            print(event['detail']['responseElements'])
            responseElements = event['detail']['responseElements']
            hostedzonename = responseElements['hostedZone']['name'][:-1]
            print("Hosted zone found is : ", hostedzonename)
            apigee_bearer_token = self.GetAPIGEEBearerToken()
            if apigee_bearer_token :
                print("APIGEE bearer token is retrieved..")
                checksubzoneurl = 'https://'+self.gridmasteragigee+'/wapi/'+self.gmapiversion+'/zone_delegated?fqdn~=^'+hostedzonename+'$&_return_fields=fqdn&_return_as_object=1' ## GET
                headers = {'Authorization': 'Bearer '+apigee_bearer_token}
                payload={}
                SZresponse = requests.request("GET", checksubzoneurl, headers=headers, data=payload)
                SZresponseResults = json.loads(SZresponse.text)
                if  SZresponse.status_code == 200 and len(SZresponseResults['result']) == 0:
                    print("retrieved the response...")
                    print(json.loads(SZresponse.text))
                    return json.loads(SZresponse.text)
                else:
                    print("Did not get the required response check subzone for create , hence sending false")
                    return False
            else:
                print("Did not retrieve the APIGEE bearer token at check subzone for create , hence sending false")
                return False
        except Exception as exception:
            print(str(exception))
            print("exception occured  at check subzone  for create hence.. returns false")
            return False

    def CheckIfSubZoneExistsExtnl (self , event):
        try:
            print("In check if SubZone exists for Extnl create......")
            print(event['detail']['responseElements'])
            responseElements = event['detail']['responseElements']
            hostedzonename = responseElements['hostedZone']['name'][:-1]
            print("Hosted zone found is : ", hostedzonename)
            apigee_bearer_token = self.GetAPIGEEBearerTokenExtnl()
            if apigee_bearer_token :
                print("APIGEE bearer token is retrieved..")
                checksubzoneurl = 'https://'+self.gridmasteragigeeExtnl+'/wapi/'+self.gmapiversionExtnl+'/zone_delegated?fqdn~=^'+hostedzonename+'$&_return_fields=fqdn&_return_as_object=1' ## GET
                headers = {'Authorization': 'Bearer '+apigee_bearer_token}
                payload={}
                SZresponse = requests.request("GET", checksubzoneurl, headers=headers, data=payload)
                SZresponseResults = json.loads(SZresponse.text)
                if  SZresponse.status_code == 200 and len(SZresponseResults['result']) == 0:
                    print("retrieved the response...")
                    print(json.loads(SZresponse.text))
                    return json.loads(SZresponse.text)
                else:
                    print("Did not get the required response check subzone for Extnl create , hence sending false")
                    return False
            else:
                print("Did not retrieve the APIGEE bearer token at check subzone for Extnl create , hence sending false")
                return False
        except Exception as exception:
            print(str(exception))
            print("exception occured  at check subzone  for Extnl create hence.. returns false")
            return False

    def CheckIfSubZoneExistsDelete (self , event):
        try:
            print("In check if SubZone exists for delete......")
            print(event['detail']['requestParameters'])
            requestElements = event['detail']['requestParameters']
            Delegation_ID = requestElements['id']
            print("Delegation_ID is : ", Delegation_ID)
            apigee_bearer_token = self.GetAPIGEEBearerToken()
            if apigee_bearer_token :
                print("APIGEE bearer token is retrieved..")
                checksubzoneurl = 'https://'+self.gridmasteragigee+'/wapi/'+self.gmapiversion+'/zone_delegated?*Delegation_ID~=^'+Delegation_ID+'$&_return_fields=fqdn&_return_as_object=1' ## GET
                headers = {'Authorization': 'Bearer '+apigee_bearer_token}
                payload={}
                CSZDresponse = requests.request("GET", checksubzoneurl, headers=headers, data=payload)
                CSZDresponseResult = json.loads(CSZDresponse.text)
                if  CSZDresponse.status_code == 200 and len(CSZDresponseResult['result']) == 1 :
                    print("retrieved the response...")
                    return json.loads(CSZDresponse.text)
                else:
                    print("Did not get the required response check subzone for delete , hence sending false")
                    return False
            else:
                print("Did not retrieve the APIGEE bearer token at check subzone  for delete, hence sending false")
                return False
        except Exception as exception:
            print(str(exception))
            print("exception occured  at check subzone  for delete hence.. returns false")
            return False

    def CheckIfSubZoneExistsDeleteExtnl (self , event):
        try:
            print("In check if SubZone exists for Extnl delete......")
            print(event['detail']['requestParameters'])
            requestElements = event['detail']['requestParameters']
            Delegation_ID = requestElements['id']
            print("Delegation_ID is : ", Delegation_ID)
            apigee_bearer_token = self.GetAPIGEEBearerTokenExtnl()
            if apigee_bearer_token :
                print("APIGEE bearer token is retrieved..")
                checksubzoneurl = 'https://'+self.gridmasteragigeeExtnl+'/wapi/'+self.gmapiversionExtnl+'/zone_delegated?*Delegation_ID~=^'+Delegation_ID+'$&_return_fields=fqdn&_return_as_object=1' ## GET
                headers = {'Authorization': 'Bearer '+apigee_bearer_token}
                payload={}
                CSZDresponse = requests.request("GET", checksubzoneurl, headers=headers, data=payload)
                CSZDresponseResult = json.loads(CSZDresponse.text)
                if  CSZDresponse.status_code == 200 and len(CSZDresponseResult['result']) == 1 :
                    print("retrieved the response...")
                    return json.loads(CSZDresponse.text)
                else:
                    print("Did not get the required response check subzone for Extnl delete , hence sending false")
                    return False
            else:
                print("Did not retrieve the APIGEE bearer token at check subzone for Extnl delete, hence sending false")
                return False
        except Exception as exception:
            print(str(exception))
            print("exception occured  at check subzone for Extnl delete hence.. returns false")
            return False

    def DelegateSubzone (self , event, Req_Ticket):
        try:
            print("Inside Delegate SubZone......")
            print(event['detail']['responseElements'])
            responseElements = event['detail']['responseElements']
            hostedzonename = responseElements['hostedZone']['name'][:-1]
            print("Hosted zone name is:", hostedzonename)
            Delegation_ID = responseElements['hostedZone']['id'].split("/")[2]
            print ("Hosted zone id to use is:" , Delegation_ID)
            externalAttribute =  { "Delegation_ID": {"value": Delegation_ID} , "Req_Date": {"value": datetime.today().strftime('%Y-%m-%d')},  "Req_Ticket": {"value": Req_Ticket} }
            print("External attributes", externalAttribute)
            nameServers = responseElements['delegationSet']['nameServers']
            print("Hosted zone name servers are:", nameServers)
            delegate_toList = []
            if nameServers:
                print("name servers found at nameServers so finding the IPs..")
                for nameServer in nameServers:
                    nspairs = {}
                    IPAddressNS = self.IPAddressNSlookUp(nameServer)
                    if IPAddressNS:
                        print("nslookup returned the IP address..")
                        nspairs.update({"address":IPAddressNS, "name":nameServer})
                    else:
                        print("nslookup did not returned the IP address..Hence exits now.")
                        return False
                    delegate_toList.append(nspairs)
            else:
                print("No name servers found at nameServers list hence exiting now..")
                return False
            apigee_bearer_token = self.GetAPIGEEBearerToken()
            if apigee_bearer_token :
                print("APIGEE bearer token is retrieved..")
                if delegate_toList :
                    print("delegate_to List IP addresses are also retrieved..")
                    delegatesubzoneurl = 'https://'+self.gridmasteragigee+'/wapi/'+self.gmapiversion+'/zone_delegated?_return_fields%2B=fqdn,delegate_to&_return_as_object=1' ## POST
                    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+apigee_bearer_token}
                    payload = json.dumps({"fqdn":hostedzonename,"delegate_to":delegate_toList, "extattrs":externalAttribute})
                    print (payload)
                    DSresponse = requests.request("POST", delegatesubzoneurl, headers=headers, data=payload)
                    if  DSresponse.status_code == 201:
                        print("retrieved the response..zone delegation is successfull..!")
                        print(json.loads(DSresponse.text))
                        return json.loads(DSresponse.text)
                    else:
                        print("Zone delegation API response is not as expected..")
                        return False
                else : 
                    print("delegate_to List IP addresses are NOT retrieved at zone delegation function..")
                    return False
            else:
                print("APIGEE bearer token did not found at delegate zone function..")
                return False
        except Exception as exception:
                print(str(exception))
                print("Run time exception occured at delegate zone function..")
                return False

    def DelegateSubzoneExtnl (self , event, Req_Ticket):
        try:
            print("Inside Delegate SubZone Extnl......")
            print(event['detail']['responseElements'])
            responseElements = event['detail']['responseElements']
            hostedzonename = responseElements['hostedZone']['name'][:-1]
            print("Hosted zone name is:", hostedzonename)
            Delegation_ID = responseElements['hostedZone']['id'].split("/")[2]
            print ("Hosted zone id to use is:" , Delegation_ID)
            externalAttribute =  { "Delegation_ID": {"value": Delegation_ID} , "Req_Date": {"value": datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')},  "Req_Ticket": {"value": Req_Ticket} }
            print("External attributes", externalAttribute)
            nameServers = responseElements['delegationSet']['nameServers']
            print("Hosted zone name servers are:", nameServers)
            delegate_toList = []
            if nameServers:
                print("name servers found at nameServers so finding the IPs..")
                for nameServer in nameServers:
                    nspairs = {}
                    IPAddressNS = self.IPAddressNSlookUpExtnl(nameServer)
                    if IPAddressNS:
                        print("nslookup returned the IP address..")
                        nspairs.update({"address":IPAddressNS, "name":nameServer})
                    else:
                        print("nslookup did not returned the IP address..Hence exits now.")
                        return False
                    delegate_toList.append(nspairs)
            else:
                print("No name servers found at nameServers list hence exiting now..")
                return False
            apigee_bearer_token = self.GetAPIGEEBearerTokenExtnl()
            if apigee_bearer_token :
                print("APIGEE bearer token Extnl is retrieved..")
                if delegate_toList :
                    print("delegate_to List IP addresses are also retrieved in Extnl..")
                    delegatesubzoneurl = 'https://'+self.gridmasteragigeeExtnl+'/wapi/'+self.gmapiversionExtnl+'/zone_delegated?_return_fields%2B=fqdn,delegate_to&_return_as_object=1' ## POST
                    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+apigee_bearer_token}
                    payload = json.dumps({"fqdn":hostedzonename,"delegate_to":delegate_toList, "extattrs":externalAttribute})
                    print (payload)
                    DSresponse = requests.request("POST", delegatesubzoneurl, headers=headers, data=payload)
                    if  DSresponse.status_code == 201:
                        print("retrieved the response..zone delegation to Extnl is successfull..!")
                        print(json.loads(DSresponse.text))
                        return json.loads(DSresponse.text)
                    else:
                        print("Zone delegation Extnl API response is not as expected..")
                        return False
                else : 
                    print("delegate_to List IP addresses are NOT retrieved at zone delegation Extnl function..")
                    return False
            else:
                print("APIGEE bearer token did not found at delegate zone Extnl function..")
                return False
        except Exception as exception:
                print(str(exception))
                print("Run time exception occured at delegate zone Extnl function..")
                return False

    def DeleteSubzoneDelegation (self , subzonereference):
        try:
            print("In delete subzone......")
            apigee_bearer_token = self.GetAPIGEEBearerToken()
            if apigee_bearer_token :
                print("APIGEE bearer token is retrieved in Delete delegation..")
                deletesubzoneurl = 'https://'+self.gridmasteragigee+'/wapi/'+self.gmapiversion+'/'+subzonereference+'?_return_as_object=1' ## DELETE
                headers = {'Authorization': 'Bearer '+apigee_bearer_token}
                payload={}
                SZDresponse = requests.request("DELETE", deletesubzoneurl, headers=headers, data=payload)
                if  SZDresponse.status_code == 200:
                    print("Response is as expected in Subzone delete function API...")
                    return json.loads(SZDresponse.text)
                else:
                    print("Did not get the required response for subzone delete , hence sending false")
                    return False
            else:
                print("Did not retrieve the APIGEE bearer token for subzone delete, hence sending false")
                return False
        except Exception as exception:
            print(str(exception))
            print("exception occured for subzone delete hence.. returns false")
            return False

    def DeleteSubzoneDelegationExtnl (self , subzonereference):
        try:
            print("In delete subzone Extnl......")
            apigee_bearer_token = self.GetAPIGEEBearerTokenExtnl()
            if apigee_bearer_token :
                print("APIGEE bearer token is retrieved in Delete delegation..")
                deletesubzoneurl = 'https://'+self.gridmasteragigeeExtnl+'/wapi/'+self.gmapiversionExtnl+'/'+subzonereference+'?_return_as_object=1' ## DELETE
                headers = {'Authorization': 'Bearer '+apigee_bearer_token}
                payload={}
                SZDresponse = requests.request("DELETE", deletesubzoneurl, headers=headers, data=payload)
                if  SZDresponse.status_code == 200:
                    print("Response is as expected in Subzone delete Extnl function API...")
                    return json.loads(SZDresponse.text)
                else:
                    print("Did not get the required response for subzone delete Extnl , hence sending false")
                    return False
            else:
                print("Did not retrieve the APIGEE bearer token for subzone delete Extnl, hence sending false")
                return False
        except Exception as exception:
            print(str(exception))
            print("exception occured for subzone delete Extnl hence.. returns false")
            return False


    def get_pem_file(self):
        try:
            print("Inside Getting Pem File")
            
            session_client = boto3.session.Session()
            secretManager_client = session_client.client('secretsmanager', region_name="us-east-1")
            get_secret_value_response = secretManager_client.get_secret_value( SecretId=self.secretarn)
            if get_secret_value_response:
                if 'SecretString' in get_secret_value_response:
                    secret = get_secret_value_response['SecretString']
                    return secret
                else:
                    decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
                    return decoded_binary_secret
        except Exception as exception:
                print(str(exception))
                print("exception occured while fetching pem file .. returns false")
                return False   


    def get_jwt_token(self, signing_key):
        try:
            print("Insider Getting JWT token")
            payload = {
            'iat': int(time.time()),
            'exp': int(time.time()) + 600,
            'iss': self.github_app_id  
            }
            resp = jwt.encode(payload, signing_key, algorithm='RS256')
            return resp
        except Exception as exception:
                print(str(exception))
                print("exception occured in getting jwt token")
                return False

    
    
    def get_installation_id(self, token):
        try:
            print("Insider installation id")
            headers = {"Authorization": "Bearer " + token}
            resp = requests.get('https://api.github.com/app/installations', headers=headers)
            token = resp.content
            token = token.decode()
            id = json.loads(token)[0]["id"]
            return id
        except Exception as exception:
                print(str(exception))
                print("exception occured in getting installtion id")
                return False
    
    
    def get_installation_token(self, token):
        try:
            print("Inside getting installation token")
            print("Inside getting access token to trigger workflow")
            installation_id = self.get_installation_id(token)
            if installation_id:
                headers = {"Authorization": "Bearer " + token,
                "Accept": "application/vnd.github.v3+json"}
                url = "https://api.github.com/app/installations/"+ str(installation_id) +"/access_tokens"
                resp = requests.post(url, headers=headers)
                return resp.content
            else:
                return False
        except Exception as exception:
                print(str(exception))
                print("exception occured in getting installtion token")
                return False
    
    
    def trigger_github_workflow(self, token, hostedzonename, value):
        try:
            print("Inside trigger workflow")
            decoded_token = token.decode()
            gh_token = json.loads(decoded_token)["token"]
            headers = {     "Content-Type": "application/json",
                            "Accept": "application/vnd.github.everest-preview+json",
                            "Authorization": "Bearer "+gh_token
                        }
            name = "TCM-Infoblox-AWS-"+hostedzonename+"-"+str(value)+"-"+str(random.randint(1, 1000))
            start_time = (datetime.today()+ timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')
            end_time = (datetime.today()+ timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
            job_url = "https://github.com/"+self.owner_name+"/"+self.repo_name+"/actions/workflows/"+self.github_workflow_id
            payload = {
                "event_type": name,
                "client_payload": {
                    "Release_Overall_Status": "success",
                    "app_name": "SGSGPSG1IB103",
                    "start-time": start_time,
                    "end-time": end_time,
                    "template-id": self.templateid,
                    "change-type": "standard",
                    "template-type": "standard_change_template",
                    "CorrelationId": name,
                    "Release_Work_Notes": {
                    "repositories": [
                        {
                        "awsatShell": {
                            "workflow_jobs": [
                            {
                                "job_name": "AWSatShell-DNS-Zone-Delegation-"+hostedzonename,
                                "job_url": job_url,
                                "job_starttime": start_time,
                                "job_endtime": end_time,
                                "job_status": "success"
                            }
                            ]
                        }
                        }
                    ]
                    }
                }
            }
            dispatch_url = "https://api.github.com/repos/"+self.owner_name+"/"+self.repo_name+"/dispatches"
            ResponseValue=requests.post(dispatch_url,data=json.dumps(payload),headers=headers)
            if  ResponseValue.status_code in [ 201, 200, 204]:
                print("retrieved the response..")
                print(ResponseValue)
                print(ResponseValue.content)
                return gh_token, name
            else:
                print(ResponseValue)
                print(ResponseValue.content)
                print("Did not get the required response") 
                return False, False
        except Exception as exception:
                print(str(exception))
                print("exception occured in triggering flow")
                return False, False
    
    def RaiseChangeRequest (self ,tasktype, hostedzonename):
        try: 
            print("In Raise Change Request......")
            print("Hosted zone name or id is:", hostedzonename)
            if tasktype == "Create":
                value = "CREATE"
            else:
                value = "DELETE"
            pem_file = self.get_pem_file()
            sign_key = bytes(pem_file, "utf-8")
            print("Type of key :- ",type(sign_key))
            if sign_key:
                jwt_token = self.get_jwt_token(sign_key)
                if jwt_token:
                   installation_token = self.get_installation_token(jwt_token)
                   if installation_token:
                        token, worklflowname = self.trigger_github_workflow(installation_token, hostedzonename, value)
                        print("Workflow triggered name is:- ", worklflowname)
                        return token, worklflowname
                   else:
                       print("There is some issue in retrieving the intsalltion token hence quiting..")
                       return False, False
                else:
                    print("There is some issue in getting jwt token or issue with pem content")
                    return False, False
            else:
                print("There is some issue in getting jwt token or issue with pem content")
                return False, False
        except Exception as exception:
            print(str(exception))
            print("exception occured when creating change returns false")
            self.Email_Transaction_Results("ChangeCreation", "FAILED", value, hostedzonename, "NoChangeCreated")
            return False, False
    
    
    def GetChangeRequestNumber (self ,token, tasktype, hostedzonename, Workflow_name):
        try:
            print("Inside getting change number")
            headers = {"Authorization": "Bearer " + token,
                    "Accept": "application/vnd.github+json",
                    "X-GitHub-Api-Version": "2022-11-28"}
            url = "https://api.github.com/repos/"+self.owner_name+"/"+self.repo_name+"/actions/workflows/"+str(self.github_workflow_id)+"/runs?created>="+str(dt.datetime.now().date())
            print(" Sleeping for 4 min. just waiting for action to be completed")
            time.sleep(360)
            resp = requests.get(url, headers=headers)
            response_content = resp.content
            decoded_content = response_content.decode()
            final_response = json.loads(decoded_content)
            total_runs = final_response["workflow_runs"]
            print("total numbers of runs recieved in response:- ",len(total_runs))
            count = 0
            for run in total_runs:
                if run["display_title"] == Workflow_name and run["conclusion"] == 'success':
                    #count += 1
                    logs_url = "https://api.github.com/repos/"+self.owner_name+"/"+self.repo_name+"/actions/runs/"+str(run["id"])+"/logs"
                    time.sleep(50)
                    run_resp = requests.head(logs_url, headers=headers)
                    print("status code", run_resp)
                    print("headers ", run_resp.headers)
                    header = run_resp.headers
                    location = header['Location']
                    print("Location of the log file", location)
                    dwld_response = urllib.request.urlretrieve(location, "/tmp/"+Workflow_name+".zip")
                    print("Log file download response:- ", dwld_response)
                    with ZipFile("/tmp/"+Workflow_name+".zip", 'r') as zObject:  
                        zObject.extract( 
                            self.job_and_steps_path, path="/tmp/")
                    zObject.close()
                    with open("/tmp/"+self.job_and_steps_path) as file:
                        for line in (file.readlines() [-10:]):
                                print("Checking Line:-  ",line)
                                if "CHG" in line:
                                    data = line[line.index("{"):line.index("}")+1]
                                    print("Json Data recieved in log:- ",data)
                                    if json.loads(data)["changeState"] == "Scheduled":
                                        number = json.loads(data)["number"]
                                        count += 1
                                    else:
                                        print("Change Might got canceled or rejected")
                                    break
                else:
                    print("Checking the next run or Change creation might got failed")
                    
            if count == 0:
                self.Email_Transaction_Results("ChangeCreation", "FAILED", tasktype, hostedzonename, "NoChangeCreated")
                return False
            print("==========Change number is =========== :- ",number)
            os.remove("/tmp/"+Workflow_name+".zip") 
            os.remove("/tmp/"+self.job_and_steps_path)
            return number
        except Exception as exception:
            print(str(exception))
            print("exception occured when getting change number")
            self.Email_Transaction_Results("ChangeCreation", "FAILED", tasktype, hostedzonename, "NoChangeCreated")
            return False
    
        
    # def RaiseChangeRequest (self ,tasktype, hostedzonename):
    #     try: 
    #         print("In Raise Change Request......")
    #         print("Hosted zone name or id is:", hostedzonename)
    #         if tasktype == "Create":
    #             value = "CREATE"
    #         else:
    #             value = "DELETE"
    #         if self.ADOAuthorizationToken and self.ADOAPIURL and self.ADOReleaseId :
    #             print("ADO Authorization Token, ADO Release Id  and ADO URL is retrieved..")
    #             payload = json.dumps({
    #                                     "definitionId": int(self.ADOReleaseId),
    #                                     "manualEnvironments": None,
    #                                     "variables": {
    #                                         "DomainNames": {
    #                                         "value": hostedzonename,
    #                                         "allowOverride": True
    #                                         },
    #                                         "Type":{
    #                                             "value": tasktype,
    #                                             "allowOverride": True
    #                                         },
    #                                         "endDate(GMT)": {
    #                                         "value": (datetime.today()+ timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S'),
    #                                         "allowOverride": True
    #                                         },
    #                                         "startDate(GMT)": {
    #                                         "value": datetime.today().strftime('%Y-%m-%d %H:%M:%S'),
    #                                         "allowOverride": True
    #                                         }
    #                                     }
    #                                     })
    #             headers = { 'Content-Type': 'application/json',
    #                         'Authorization': 'Basic '+self.ADOAuthorizationToken
    #                     }
    #             CRresponse = requests.request("POST", self.ADOAPIURL, headers=headers, data=payload)
    #             if  CRresponse.status_code == 200:
    #                 print("Change request created successfully..")
    #                 return json.loads(CRresponse.text)
    #             else:
    #                 print("Change request creation failed..")
    #                 self.Email_Transaction_Results("ChangeCreation", "FAILED", value, hostedzonename, "NoChangeCreated")
    #                 return False
    #         else:
    #             print("Required ADO URL , ADO Release Id and Token not retrieved hence returns false..")
    #             self.Email_Transaction_Results("ChangeCreation", "FAILED", value, hostedzonename, "NoChangeCreated")
    #             return False
    #     except Exception as exception:
    #         print(str(exception))
    #         print("exception occured when creating change returns false")
    #         self.Email_Transaction_Results("ChangeCreation", "FAILED", value, hostedzonename, "NoChangeCreated")
    #         return False

    # def CheckChangeRequestCreationStatus (self , tasktype, hostedzonename, releasenumber):
    #     try: 
    #         print("In Check change request creation state......")
    #         print("Hosted zone name or id is:", hostedzonename)
    #         if tasktype == "Create":
    #             value = "CREATE"
    #         else:
    #             value = "DELETE"
    #         if self.ADOAuthorizationToken and self.ADOAPIURL :
    #             print("ADO Authorization Token and ADO URL is retrieved..")
    #             payload = {}
    #             headers = { 'Content-Type': 'application/json',
    #                         'Authorization': 'Basic '+self.ADOAuthorizationToken
    #                     }
    #             FinalURL = self.ADOAPIURL.replace("?", '/'+str(releasenumber)+'?')
    #             print("Final API URL in Check Change status is:", FinalURL)
    #             CRSresponse = requests.request("GET", FinalURL, headers=headers, data=payload)
    #             if  CRSresponse.status_code == 200:
    #                 print("Change request status check retrieved successfully..")
    #                 return json.loads(CRSresponse.text)
    #             else:
    #                 print("Change request status check failed..")
    #                 self.Email_Transaction_Results("ChangeCreationStatus", "FAILED", value, hostedzonename, "NoChangeCreated")
    #                 return False
    #         else:
    #             print("Required ADO URL and Token not retrieved hence returns false in Change request status check..")
    #             self.Email_Transaction_Results("ChangeCreationStatus", "FAILED", value, hostedzonename, "NoChangeCreated")
    #             return False
    #     except Exception as exception:
    #         print(str(exception))
    #         print("exception occured when creating change returns false in Change request status check")
    #         self.Email_Transaction_Results("ChangeCreationStatus", "FAILED", value, hostedzonename, "NoChangeCreated")
    #         return False

    # def GetChangeRequestNumber (self ,tasktype, hostedzonename, releasenumber, envnumber, deployphasenumber):
    #     try: 
    #         print("In Get Change request number......")
    #         print("Hosted zone name or id is:", hostedzonename)
    #         if tasktype == "Create":
    #             value = "CREATE"
    #         else:
    #             value = "DELETE"
    #         if self.ADOAuthorizationToken:
    #             print("ADO Authorization token is retrieved..")
    #             payload = {}
    #             headers = { 'Content-Type': 'application/json',
    #                         'Authorization': 'Basic '+self.ADOAuthorizationToken
    #                     }
    #             FinalURL = 'https://vsrm.dev.azure.com/sede-it-itso/Infoblox/_apis/release/releases/'+str(releasenumber)+'/environments/'+str(envnumber)+'/deployPhases/'+str(deployphasenumber)+'/tasks/3/logs?api-version=7.1-preview.2'
    #             print("Final API URL in Get Change number is:", FinalURL)
    #             GCRNresponse = requests.request("GET", FinalURL, headers=headers, data=payload)
    #             if  GCRNresponse.status_code == 200:
    #                 print("Get Change request number retrieved successfully..")
    #                 return json.loads((GCRNresponse.text.strip().split("\n")[-1]).strip().split("Response: ")[1])['result'][0]['number']
    #             else:
    #                 print("Get Change request number check failed..")
    #                 self.Email_Transaction_Results("GetChangeNumber", "FAILED",value, hostedzonename, "NoChangeCreated")
    #                 return False
    #         else:
    #             print("Required Authorization Token not retrieved hence returns false in Get Change request number..")
    #             self.Email_Transaction_Results("GetChangeNumber", "FAILED",value, hostedzonename, "NoChangeCreated")
    #             return False
    #     except Exception as exception:
    #         print(str(exception))
    #         print("exception occured in Get Change request number")
    #         self.Email_Transaction_Results("GetChangeNumber", "FAILED",value, hostedzonename, "NoChangeCreated")
    #         return False

    def SNS_Alerts(self , RunStage, Status, RequestType, ResourceID, ChangeNumber):
        try:
            print("Sending email now....")
            sns_subject = 'AWS@Shell Public Account DNS zone Delegation request is processed now.'
            sns_message = 'Hello User, \n' \
                              '\n' \
                              'Below are the processed details and results of AWS@Shell DNS Zone Delegation task: \n'\
                              'Request Type :' + RequestType + '\n' \
                              'Status of request :' + Status + '\n' \
                              'Request processed stage :' + RunStage + '\n' \
                              'Resource ID :' + ResourceID + '\n' \
                              'Account Number :' + self.accountNumber + '\n' \
                              'Change Number :' + ChangeNumber + '\n' \
                              '\n' \
                            'Best regards \n'\
                            'AWS@Shell Team. \n'
            print(sns_message)
            send_response = self.sns_client.publish(TopicArn=self.sns_topic_arn, Message=sns_message, Subject=sns_subject)
            print(send_response)
            return send_response
        except Exception as e:
            print(str(e))
            return str(e)

    def Email_Transaction_Results(self , RunStage, Status, RequestType, ResourceID, ChangeNumber):
        try:
            #infoblox_dl =  "GX-ITSO-SOM-ET-CON-LAN@shell.com"
            print("Sending email now....")
            session_client = boto3.session.Session()
            ses_client = session_client.client('ses', region_name="us-east-1", aws_access_key_id=self.DNSSESKeyEmail, aws_secret_access_key=self.DNSSESSecrtEmail)
            # The email body for recipients with non-HTML email clients.
            body_text = """
                Hello Team,
                
                Below are the processed details and results of AWS@Shell DNS Zone Delegation task:          
                    * Request Type : """ + RequestType + """
                    * Status of request : """ + Status + """
                    * Request processed stage : """ + RunStage + """
                    * Resource ID : """ + ResourceID + """
                    * Account Number : """ + self.accountNumber + """
                    * Change Number : """ + ChangeNumber + """
                ACTION: If the status of request is FAIL please check with GX-SITI-CPE-Team-Titan@shell.com
                
                Best Regards,
                AWS@Shell Team
                """

            # The HTML body of the email.
            body_html = """<html>
                <head>
                <style>
                    table, td {
                    border: 1px solid black;
                    border-collapse: collapse;
                    }
                    
                    
                    th {
                    border: 1px solid black;
                    border-collapse: collapse;
                    font-weight: bold
                    }
                    
                    
                    td, th {
                    padding-left: 15px;
                    text-align: left;
                    }
                </style>
                </head>
                <body>
                <p style="font-family:'Futura Medium'">Hello Team,</p>
                <p style="font-family:'Futura Medium'">Below are the processed details and results of AWS@Shell DNS Zone Delegation task:</p>
                
                <table style="width:100%">
                    <col style="width:50%">
                    <col style="width:50%">
                    <tr bgcolor="yellow">
                        <td width="50%">Event Property Names</td>
                        <td width="50%">Event Values</td>
                    </tr>
                    <tr>
                    <td width="50%">Request Type </td>
                    <td width="50%">""" + RequestType + """</td>
                    </tr>
                    <tr>
                    <td width="50%">Status of request</td>
                    <td width="50%">""" + Status + """</td>
                    </tr>
                    <tr>
                    <td width="50%">Request processed stage</td>
                    <td width="50%">""" + RunStage + """</td>
                    </tr>
                    <tr>
                    <td width="50%">Resource ID</td>
                    <td width="50%">""" + ResourceID + """</td>
                    </tr>
                    <tr>
                    <td width="50%">Account Number</td>
                    <td width="50%">""" + self.accountNumber + """</td>
                    </tr>
                    <tr>
                    <td width="50%">Change Number</td>
                    <td width="50%">""" + ChangeNumber + """</td>
                    </tr>
                </table>

                <p style="font-family:'Futura Medium'"> ACTION: If the status of request is FAIL please check with GX-SITI-CPE-Team-Titan@shell.com</p>
                
                <p style="font-family:'Futura Medium'">Best Regards,</p>
                <p style="font-family:'Futura Medium'">AWS@Shell Team</p>
                </body>
                </html>
                """
            # Provide the contents of the email.
            send_mail_response = ses_client.send_email(
                Source="SITI-CLOUD-SERVICES@shell.com",
                Destination={
                    'ToAddresses': ["GX-ITSO-SOM-ET-CON-LAN@shell.com", self.platform_Custodian_dl, "GX-SITI-CPE-Team-Titan@shell.com", self.platform_dl]
                },
                Message={
                    'Subject': {
                        'Data': "AWS@Shell Public Account DNS zone Delegation request is processed now."

                    },
                    'Body': {
                        'Text': {
                            'Data': body_text

                        },
                        'Html': {
                            'Data': body_html

                        }
                    }
                }
            )
            print(send_mail_response)
            return send_mail_response
        except Exception as e:
            print(str(e))
            return str(e)

def lambda_handler(event, context):
    """"
    # AWS@Shell Public Account DNS Zone Delegation to Shell Infoblox
    """
    create_dndelegation_obj = DNSDelegation(event, context)
    try:
        print("Event {}".format(event))
        print("Job started now......")
        if event['detail']['eventName'] == "CreateHostedZone":
            responseElements = event['detail']['responseElements']
            hostedzonename = responseElements['hostedZone']['name'][:-1]
            print("Hosted zone name is:", hostedzonename) 
            hosted_id = responseElements['hostedZone']['id'].split('/')[-1]
            zone_split_list= hostedzonename.split('.')
            root_domain_list= zone_split_list[-2:]
            root_domain= '.'.join(root_domain_list)
            if(len(zone_split_list)>3 or root_domain.lower() != 'shell.com'):
                print('Dns Zone Delegation not required for HostedZone = {}'.format(hostedzonename))
            else:
                print("Hosted Zone Delegation creation....Checking if parent zone exists.")
                if create_dndelegation_obj.CheckIfParentZoneExists(event):
                    print("Parentzone exists in internal Infoblox GM ..")
                    if create_dndelegation_obj.CheckIfParentZoneExistsExtnl(event):
                        print("Parentzone exists in External Infoblox GM..")
                        ResultIfSubZoneExists = create_dndelegation_obj.CheckIfSubZoneExists(event)
                        if len(ResultIfSubZoneExists['result']) == 0:
                            print("Subzone does not exists in Internal Infoblox GM hence check in external also..")
                            ResultIfSubZoneExistsExtnl = create_dndelegation_obj.CheckIfSubZoneExistsExtnl(event)
                            if len(ResultIfSubZoneExistsExtnl['result']) == 0:
                                print("Subzone does not exists in External Infoblox GM also hence creating change now for delegation..")
                                result_token, workflow_run_name = create_dndelegation_obj.RaiseChangeRequest("Create", hosted_id)
                                if result_token and workflow_run_name:
                                        GetChangeNumber = create_dndelegation_obj.GetChangeRequestNumber(result_token, "CREATE", hostedzonename, workflow_run_name)
                                        if GetChangeNumber :
                                            print ("Change Number retrieved successfully.. Now Delegating zone..")
                                            SubzoneDelegationResults = create_dndelegation_obj.DelegateSubzone(event, GetChangeNumber)
                                            if SubzoneDelegationResults :
                                                print("Subzone {} delegated to Shell Internal infoblox successfully..!!!!".format(hostedzonename))
                                                print("Now delegating to external..")
                                                SubzoneDelegationResultsExtnl = create_dndelegation_obj.DelegateSubzoneExtnl(event, GetChangeNumber)
                                                if SubzoneDelegationResultsExtnl :
                                                    print("Subzone {} delegated to Shell External infoblox successfully..!!!!".format(hostedzonename))
                                                    create_dndelegation_obj.Email_Transaction_Results("DelegateZone", "SUCCESS","CREATE", hostedzonename, GetChangeNumber)
                                                else:
                                                    print("Unfortunately subzone delegation to External GM falied..")
                                                    create_dndelegation_obj.Email_Transaction_Results("DelegateZoneExternal", "FAILED","CREATE", hostedzonename, GetChangeNumber)
                                            else:
                                                print("Unfortunately subzone delegation to Internal GM falied..")
                                                create_dndelegation_obj.Email_Transaction_Results("DelegateZoneInternal", "FAILED","CREATE", hostedzonename, GetChangeNumber)
                                        else:
                                            print("Change number not retrived.. hence sending notification..")
                                else:
                                    print("Change creation failed..")
                            else:
                                print("Subzone already exist in External Infoblox GM..")
                                create_dndelegation_obj.Email_Transaction_Results("CheckIfSubZoneExistsExternal", "FAILED","CREATE",hostedzonename, "NoChangeCreated")
                        else:
                            print("Subzone already exist in Internal Infoblox GM..")
                            create_dndelegation_obj.Email_Transaction_Results("CheckIfSubZoneExistsInternal", "FAILED","CREATE",hostedzonename, "NoChangeCreated")
                    else:
                        print("Parentzone does not exists in Exeternal Infoblox GM hence sending notification")
                        create_dndelegation_obj.Email_Transaction_Results("CheckIfParentZoneExistsExternal", "FAILED","CREATE",hostedzonename, "NoChangeCreated")
                else :
                    print("Parentzone does not exists in internal Infoblox GM hence sending notification")
                    create_dndelegation_obj.Email_Transaction_Results("CheckIfParentZoneExistsInternal", "FAILED","CREATE",hostedzonename, "NoChangeCreated")

        elif event['detail']['eventName'] == "DeleteHostedZone":
            print("Hosted Zone Delegation deletion....Checking if subzone delegated.")
            requestElement = event['detail']['requestParameters']
            hostedzoneid = requestElement['id']
            print("Hosted zone deleted id is:", hostedzoneid)
            CheckDeleteSubzone =  create_dndelegation_obj.CheckIfSubZoneExistsDelete(event)
            if len(CheckDeleteSubzone['result']) == 1:
                print("Subzone is delegated at Shell Infoblox Internal, now it will be checked in external as well.")
                CheckDeleteSubzoneExtnl =  create_dndelegation_obj.CheckIfSubZoneExistsDeleteExtnl(event)
                if len(CheckDeleteSubzoneExtnl['result']) == 1:
                    print("Subzone is delegated at Shell Infoblox external as well.")
                    print("Subzone deletion change creation..")
                    result_token, workflow_run_name = create_dndelegation_obj.RaiseChangeRequest("Delete", hostedzoneid)
                    if result_token and workflow_run_name:
                        print("Change creation invoked successfully, checking the status now..")
                        
                        GetChangeNumber = create_dndelegation_obj.GetChangeRequestNumber(result_token, "Delete", hostedzoneid, workflow_run_name)
                        if GetChangeNumber :
                            print ("Change Number retrieved successfully.. Now deleting subzone delegation in infoblox..")
                            SubzoneDelegationDeleteResults = create_dndelegation_obj.DeleteSubzoneDelegation(CheckDeleteSubzone['result'][0]['_ref'])
                            if SubzoneDelegationDeleteResults :
                                print("Subzone id {} is deleted from Shell infoblox Internal GM successfully..!!!!".format(hostedzoneid))
                                print("Now deleting delegation from external GM..")
                                SubzoneDelegationDeleteResultsExtnl = create_dndelegation_obj.DeleteSubzoneDelegationExtnl(CheckDeleteSubzoneExtnl['result'][0]['_ref'])
                                if SubzoneDelegationDeleteResultsExtnl :
                                    print("Subzone id {} is deleted from Shell infoblox external GM successfully..!!!!".format(hostedzoneid))
                                    create_dndelegation_obj.Email_Transaction_Results("DeleteDelegatedZone", "SUCCESS","DELETE", hostedzoneid, GetChangeNumber)
                                    print("subzone delegation deletion successful for subzone id: ", hostedzoneid)
                                else:
                                    print("Unfortunately External subzone delegation deletion falied..")
                                    create_dndelegation_obj.Email_Transaction_Results("DeleteDelegatedZoneExternal", "FAILED","DELETE", hostedzoneid, GetChangeNumber)
                            else:
                                print("Unfortunately Internal subzone delegation deletion falied..")
                                create_dndelegation_obj.Email_Transaction_Results("DeleteDelegatedZoneInternal", "FAILED","DELETE", hostedzoneid, GetChangeNumber)
                        else:
                            print("Change number not retrived.. hence sending notification..")
                    else:
                        print("Change creation failed..")
                else:
                    print("Subzone is not delegated to Shell infoblox External GM.. Hence doing nothing for delete")
            else:
                print("Subzone is not delegated to Shell infoblox internal GM.. Hence doing nothing for delete")
        else:
            print("Not required action on Route53 service..")
        print("Job completed now......!!")
    except Exception as exception:
        print("Exception in Lambda Handler", exception)