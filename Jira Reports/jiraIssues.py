
############################################################

# Note:-

# Below mentioned custom fields will change for each JIRA INSTANCES. Either get it from JIRA Admin or get it from web inspect
# Below is to update the DB about JIRA ISSUE and S3 code is commented out. Please use accordingly
###############


from jira import JIRA
import json
import requests
import base64
import boto3
from datetime import date
import csv
import os
import sys
import psycopg2
# query = 'project = "<project name>" and "vuln found date[date]" >= "2024-01-01" ORDER BY created DESC'

def get_secret(secretarn):
    '''
    This function returns the secrets
    '''
    try:
        
        session_client = boto3.session.Session()
        sm_client = session_client.client('secretsmanager', region_name='us-east-1')
        sm_response = sm_client.get_secret_value( SecretId=secretarn)
        if sm_response:
            if "SecretString" in sm_response:
                secret = sm_response['SecretString']
                return secret
            else:
                decoded_secret = base64.b64decode(sm_response['SecretBinary'])
                return decoded_secret
    except Exception as ex:
        print("something went wrong in retirving secret")
        raise ex


def get_query(project, formatted_date, issuetype):
    '''
    This will frame the query based 
    '''
    try:
        #print("Inside get query")
        query = 'project = '+project +' and issuetype in ("'+issuetype+'")'
        #query = 'project = '+project +' and "vuln found date[date]" >='+ formatted_date +' and type in ("DAST Issue", "External Vendor Pentest") ORDER BY created DESC'
        print("Query is :- ",query)
        return query
    except Exception as ex:
        print("something went wrong in getting the query")
        raise ex
def close_conn_cur(cur,conn):
    cur.close()
    conn.close()

def set_the_datebase(table_headers,resourcetype):
    try:
        secretarn = "XXX"
        db_host = "YYYY"
        db_port = "5432"
        db_name = "XXX"
        db_user = "XXX"
        db_password = json.loads(get_secret(secretarn))['vmp_pentest_etl_add_data']
        
        conn = psycopg2.connect(host=db_host, port=db_port, dbname=db_name, user=db_user, password=db_password)
        cur = conn.cursor()
        query = f"""CREATE TABLE IF NOT EXISTS pentest.{resourcetype.replace(" ","")} {table_headers}"""
        cur.execute(query)
        conn.commit()
        #print(type(f"""CREATE TABLE IF NOT EXISTS ics.{resourcetype} {table_headers}"""))
        cur.execute(f"""TRUNCATE TABLE pentest.{resourcetype.replace(" ","")}""")
        print("Database Connected")
        return conn, cur
    except Exception as ex:
        print(ex)
        raise ex
    
def insert_into_datebase(row,resourcetype,table_headers):
    try:
        conn,cur = set_the_datebase(table_headers,resourcetype)
        #print(f"""Query is:- \n ______________________\nINSERT INTO ics.{resourcetype} VALUES """+str(row))
        #print(type("""INSERT INTO ics.{resourcetype} VALUES """+str(row)))
        insertquery = f"""INSERT INTO pentest.{resourcetype.replace(" ","")} VALUES """+str(row)
        cur.execute(insertquery)
        #cur.execute(f"""INSERT INTO ics.{resourcetype} """+"""VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",row)
        conn.commit()
        close_conn_cur(cur,conn)
        return True
    except Exception as ex:
        print(ex)
        print(row)
        raise ex

# def upload_to_s3(row, formatted_date,issuetype):
#     '''
#     This function creates a file and upload to s3 bucket
#     '''
#     try:
#         #print("Inside s3 bucket")
#         issuetype = issuetype.replace(" ","_")
#         s3 = boto3.resource('s3')
#         bucket = 'jiraissue'
#         year = formatted_date.split('-')[0]
#         month = formatted_date.split('-')[1]
#         day = formatted_date.split('-')[2]
#         key = 'Jira/'+year+'/'+month+'/'+day+'/'
#         with open('/tmp/vuln_jira_issues.csv', 'a') as jirafile:
#             writer = csv.writer(jirafile)
#             writer.writerow(['Number','Title','CreatedDate','UpdatedDate','IssueType','Status','Resolved Date','Risk ID','Asignee','Priority','Application ID','Labels','Product Owner','Techincal Owner','Techinal COntacts','Reporter','URL','PenTest Vendor','Vuln Name','Vuln ID'])
#             writer.writerows(row)
#         jirafile.close()
#         s3.Bucket(bucket).upload_file("/tmp/vuln_jira_issues.csv", key+issuetype+'_vuln_jira_issues.csv')
#         os.remove('/tmp/vuln_jira_issues.csv')
#         return True
#     except Exception as ex:
#         print("There is something went wrong in uploading s3 bucket")
#         raise ex

def lambda_handler(event, context):
    '''
    This lambda will fetch the jira issue and puts into a s3 bucket / DB
    '''
    try:
        #issuetype = event['issuetype']
        issuetype = sys.argv[1]
        secretarn = "ZZZZZZZ"
        json_secrets = get_secret(secretarn)
        secret = json.loads(json_secrets)
        url = secret['url']
        apiToken = secret['apiToken']
        email = secret['email']
        project = secret['Project']
        jira_auth = JIRA(url,basic_auth=(email, apiToken))
        issues_list = []
        start = 0
        mxmum = 100
        today = date.today()
        formatted_date = today.strftime("%Y-%m-%d")
        #formatted_date = "2024-01-01"
        query = get_query(project, formatted_date, issuetype)
        while True:
            all_issues_queried = jira_auth.search_issues(query, startAt=start, maxResults=mxmum)
            issues_list.extend(all_issues_queried)
            if len(all_issues_queried) < mxmum:
                break
            start += mxmum
        # print("List of recieved issues :- {}".format(issues_list))
        # print("Number of recieved issues :- {}".format(len(issues_list)))
        if len(issues_list) > 0:
            dict_file = {}
            #row =[]
            rows = ""
            for issue in issues_list:
                try:
                    issue_details = jira_auth.issue(issue.key)
                    #print("Checking the ID:- {}".format(issue.key))
                    number = issue.key
                    title = issue_details.fields.summary
                    created_date = issue_details.fields.created
                    if 'updated' in issue_details.fields.__dict__.keys():
                        updated_date = issue_details.fields.__dict__['updated']
                    else:
                        updated_date = ''
                    issuetype = issue_details.fields.issuetype.name
                    status = issue_details.fields.status.name
                    
                    if status == 'Risk Exception':
                        if 'customfield_10102' in issue_details.fields.__dict__.keys() and issue_details.fields.__dict__['customfield_10102'] != None:
                            riskid = issue_details.fields.__dict__['customfield_10102']
                        else:
                            riskid = ''
                    else:
                        riskid = ''
                    if issue_details.fields.assignee == None:
                        assignee = 'N/A'
                    else:
                        assignee = issue_details.fields.assignee.displayName
                    priority = issue_details.fields.priority.name
                    res_date = issue_details.fields.resolutiondate
                    if res_date == None:
                        res_date = ''
                    if 'customfield_10120' in issue_details.fields.__dict__.keys() and issue_details.fields.__dict__['customfield_10120'] != None:
                        applicationid = issue_details.fields.__dict__['customfield_10120']
                    else:
                        applicationid = ''
                    labels = issue_details.fields.labels
                    # productOwner = ''
                    # techincalOwner = ''
                    if 'customfield_10110' in issue_details.fields.__dict__.keys() and issue_details.fields.__dict__['customfield_10110'] != None :
                        productOwner = issue_details.fields.__dict__['customfield_10110'].displayName
                    else:
                        productOwner = ''
                    if 'customfield_11649' in issue_details.fields.__dict__.keys() and issue_details.fields.__dict__['customfield_11649'] != None:
                        techincalOwner = issue_details.fields.__dict__['customfield_11649'].displayName
                    else:
                        techincalOwner = ''
                    if 'customfield_10855' in issue_details.fields.__dict__.keys() and issue_details.fields.__dict__['customfield_10855'] != None:
                        TechnicalCOntacts = issue_details.fields.__dict__['customfield_10855'].displayName
                    else:
                        TechnicalCOntacts = ''
                    reporter = issue_details.fields.reporter.displayName
                    if 'customfield_10611' in issue_details.fields.__dict__.keys() and issue_details.fields.__dict__['customfield_10611'] != None:
                        url = issue_details.fields.__dict__['customfield_10611']
                    else:
                        url = ''
                    if 'customfield_10900' in issue_details.fields.__dict__.keys() and issue_details.fields.__dict__['customfield_10900'] != None:
                        pentestVendor = issue_details.fields.__dict__['customfield_10900'].value
                    else:
                        pentestVendor = ''
                    if 'customfield_10901' in issue_details.fields.__dict__.keys() and issue_details.fields.__dict__['customfield_10901'] != None:
                        resolve_date = issue_details.fields.__dict__['customfield_10901']
                    else:
                        resolve_date = ''
                    if 'customfield_10851' in issue_details.fields.__dict__.keys() and issue_details.fields.__dict__['customfield_10851'] != None:
                        vulnName = issue_details.fields.__dict__['customfield_10851']
                    else:
                        vulnName = ''
                    if 'customfield_10893' in issue_details.fields.__dict__.keys() and issue_details.fields.__dict__['customfield_10893'] != None:
                        vulnID = issue_details.fields.__dict__['customfield_10893']
                    else:
                        vulnID = ''
                    row = (str(number),title.replace('"', '').replace("'", ''),str(created_date),str(updated_date),issuetype,status,str(res_date),str(riskid),assignee.replace("'", ''),priority,str(applicationid),",".join(labels),productOwner.replace("'", ''),techincalOwner.replace("'", ''),TechnicalCOntacts.replace("'", ''),reporter.replace("'", ''),url.replace("'", ''),pentestVendor,vulnName.replace('"', '').replace("'", ''),vulnID)
                    rows = rows+str(row)+","
                    #row.append([number,title,created_date,updated_date,issuetype,status,res_date,riskid,assignee,priority,applicationid,labels,productOwner,techincalOwner,TechnicalCOntacts,reporter,url,pentestVendor,resolve_date,vulnName,vulnID])
                except Exception as ex:
                    print(ex)
                    print(issue.key)
                    print("==================")
                    print(issue_details.fields.__dict__.items())
            rows = rows[:-1]
            table_headers = """(Number text,
                                Title text,
                                CreationDate text,
                                UpdatedDate text,
                                Type text,
                                Status text,
                                ResolutionDate text,
                                RiskID text,
                                Assigne text,
                                Priority text,
                                ApplicationID text,
                                Labels text,
                                ProductOwner text,
                                TechincalOwner text,
                                TechincalContacts text,
                                Reporter text,
                                URL text,
                                PentestVendor text,
                                VulnName text,
                                VulnID text
                                )"""
            db_response = insert_into_datebase(rows, issuetype,table_headers)
            if not db_response:
                print("something went wrong in inserting the values")
            #status = upload_to_s3(row, formatted_date,issuetype)
            return db_response
        
        else:
            print("There are no issues raised for the date")
            return True 
    except Exception as ex:
        print("There is something went wrong in lambda handler:- {}".format(ex))
        raise ex



lambda_handler('jira','issues')