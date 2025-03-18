# Rego Template 

## Brief overview of Wiz

Wiz is an environment management framework which consists of a Python API and a command line tool. It can be used to run a command within a deterministic environment resolved from one or several package requests
https://wiz.readthedocs.io/en/latest/introduction.html

## Custom Rego Writing Policy Style guide

Rego Policies are written in the Rego playground and in the WIZ tool. Rego policies have two native types one is EY Custom Native and another is WIZ native. EY Custom policies are the policies which are designed by EY resources. WIZ native are in build policies in WIZ.  Following are the efficient way for writing Rego. 
 
## Helpful links
[The Rego Playground (openpolicyagent.org)](https://play.openpolicyagent.org/) - For testing rego policies
[Wiz - Cloud Configuration Rules | Wiz Portal ](https://app.wiz.io/policies/cloud-configuration-rules#~(filters~(serviceType~(equals~(~'AWS))~search~(contains~'d))))- For deploying and testing custom policies
[EY Requirement Worksheet which contains custom and native policies EY_Innovation_Project Tracker_Master.xlsx (sharepoint.com)](https://eyus.sharepoint.com/:x:/r/sites/EYCloudSecurityInnovationInitiative/_layouts/15/Doc.aspx?sourcedoc=%7BC8D788F8-8471-4C9F-A13B-FE81E6607336%7D&file=EY_Innovation_Project%20Tracker_Master.xlsx&action=default&mobileredirect=true) . Excel sheet for Custom and Native policies.
https://www.wiz.io/ Information Related to WIZ 
## Example of a well written rego
![image](https://user-images.githubusercontent.com/106724271/187544061-cd70171a-98eb-4ab3-a580-517c2c005b4f.png)

## How to write policies
<https://www.openpolicyagent.org/docs/v0.13.5/how-do-i-write-policies/>
## Examples of what needs to be covered

The standard REGO policy should start with description of the requirement (RULE) as shown in the example below.

![image](https://user-images.githubusercontent.com/111082407/189767407-72d5c1bf-dfe0-4fbb-a971-1f930750574c.png)

#Follow the structure of the custom rule
 
1.	Description of the requirement
2.	Import Wiz Package
3.	Default condition
4.	Policy Logic < See Example > below:

5.	 ![image](https://user-images.githubusercontent.com/111082407/189767324-14248587-d6c8-4ca5-b3d2-82e6684ddfc2.png)
 
6. Policy body should have pass and fail condition depending on requirement. 

7. Current Configuration and expected configuration 
 
Required * 
1.	Access to Wiz to test or deploy the custom policy 
## Process to get access to Wiz:
Write email to Ilyah or Shash to get access to wiz portal

2.	Please refer below Test Data files to test the custom  wiz rules 
S3 Test Data  <https://github.com/ey-org/cloudsec-baseline-management/pull/320/files#diff-155dbf121596e1767b5e7dfc00646a5bbdf71fa76f416d84dd43d965f601457f>
 
## How to test once it's completed
<https://www.openpolicyagent.org/docs/v0.13.5/how-do-i-test-policies/>
(Working with GDS team to develop startegy for testing Custom Regos without deploying resources )


## High-level styleguide (do's and don'ts)

![image](https://user-images.githubusercontent.com/106724271/189973720-bb52e5b5-b46f-4761-92da-435f4ea71327.png)

In the above REGO structure we should also consider parameters outside the scope. To be more specific here access key last date can be not applicable . So we have to think briefly in order to get perfect expected outputs.

Another aspect is also consider case sensetivity of REGO policies 


