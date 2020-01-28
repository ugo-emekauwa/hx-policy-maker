"""
HyperFlex Edge Policy Maker for Cisco Intersight Script on dCloud (All Flash, 2-Node), v1.0
Author: Ugo Emekauwa
Contact: uemekauw@cisco.com, uemekauwa@gmail.com
Summary: The HyperFlex Edge Policy Maker script automates creation of sample HyperFlex policies in Intersight that can be used to deploy a HyperFlex Edge cluster.
Notes: Tested on Intersight API Reference v1.0.9-1229
"""

# Import needed Python modules
import sys
import json
import requests
import os
import logging
import datetime
import xml.etree.ElementTree as et
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
import intersight
from intersight.intersight_api_client import IntersightApiClient

# Define time variable
get_date = datetime.datetime.now()
date = get_date.strftime("%m/%d/%Y %H:%M:%S")

# Setup Logging
logging.basicConfig(filename="c:\\dcloud\\intersight_hx_policy_creator.log", level=logging.DEBUG, format="%(asctime)s %(message)s")
logging.info("Starting the Intersight Policy Set Creator for HyperFlex Edge Script.")

# Parse dCloud session.xml file to determine assigned HyperFlex Edge cluster and assign to variable
session_xml = et.parse("c:\\dcloud\\session.xml")

# Create needed variables from session.xml file
cluster_name = session_xml.find("devices/device/name").text
datacenter_name = session_xml.find("datacenter").text

# Parse matching cluster.xml file based on assigned HyperFlex Edge cluster
if cluster_name == "HyperFlex HXAF220c M5 Cluster 01":
  cluster_xml = et.parse("c:\\Scripts\\Clusters\\" + datacenter_name + "\\HyperFlex HXAF220c M5 Cluster 01\\XML_File\\cluster01.xml")
if cluster_name == "HyperFlex HXAF220c M5 Cluster 02":
  cluster_xml = et.parse("c:\\Scripts\\Clusters\\" + datacenter_name + "\\HyperFlex HXAF220c M5 Cluster 02\\XML_File\\cluster02.xml")
if cluster_name == "HyperFlex HXAF220c M5 Cluster 03":
  cluster_xml = et.parse("c:\\Scripts\\Clusters\\" + datacenter_name + "\\HyperFlex HXAF220c M5 Cluster 03\\XML_File\\cluster03.xml")

# Create needed variables from cluster.xml file
intersight_account_name = cluster_xml.find("account/intersight_account").text
intersight_account_email = cluster_xml.find("account/cisco_account/email").text
intersight_account_cluster = cluster_xml.find("platform_name").text
intersight_account_service_type = cluster_xml.find("account/service_account_type").text
intersight_account_session = session_xml.find("id").text
intersight_account_location = cluster_xml.find("datacenter").text

# Define Intersight SDK IntersightApiClient variables
# Tested on Cisco Intersight API Reference v1.0.9-1229
key_id = cluster_xml.find("account/api_keys/key01/api_key_id").text
key = "C:\\Scripts\\Clusters\\" + datacenter_name + "\\" + cluster_name + "\\Intersight_Service_Account\\API_Keys\\key01\\SecretKey.txt"
base_url = "https://intersight.com/api/v1"
api_instance = IntersightApiClient(host=base_url,private_key=key,api_key_id=key_id)


# Establish Intersight Universal Functions

def iu_get(api_path):
  """This is a function to perform a universal or generic GET on objects under available Intersight API types,
  including those not yet defined in the Intersight SDK for Python. An argument for the API type path is required.

  Args:
    api_path: The path to the targeted Intersight API type. For example, to specify the Intersight API type for
      adapter configuration policies, enter "adapter/ConfigPolicies". More API types can be found in the Intersight
      API reference library at https://intersight.com/apidocs/introduction/overview/.

  Returns:
    A dictionary containing all objects of the specified API type. If the API type is inaccessible, an
    implicit value of None will be returned.
  """
  full_resource_path = "/" + api_path
  try:
    api_instance.call_api(full_resource_path,"GET")
    response = api_instance.last_response.data
    results = json.loads(response)
    logging.info("The API resource path '" + api_path + "' has been accessed successfully.")
    return results
  except:
    logging.info("Unable to access the API resource path '" + api_path + "'.")


def iu_get_moid(api_path,moid):
  """This is a function to perform a universal or generic GET on a specified object under available
  Intersight API types, including those not yet defined in the Intersight SDK for Python. An argument for the
  API type path and MOID (managed object identifier) is required.
  
  Args:
    api_path: The path to the targeted Intersight API type. For example, to specify the Intersight API type for
      adapter configuration policies, enter "adapter/ConfigPolicies". More API types can be found in the Intersight
      API reference library at https://intersight.com/apidocs/introduction/overview/.
    moid: The managed object ID of the targeted API object.

  Returns:
    A dictionary containing all parameters of the specified API object. If the API object is inaccessible, an
    implicit value of None will be returned.
  """
  full_resource_path = "/" + api_path + "/" + moid
  try:
    api_instance.call_api(full_resource_path,"GET")
    response = api_instance.last_response.data
    results = json.loads(response)
    logging.info("The object located at the resource path '" + full_resource_path + "' has been accessed succesfully.")
    return results
  except:
    logging.info("Unable to access the object located at the resource path '" + full_resource_path + "'.")


def iu_delete_moid(api_path,moid):
  """This is a function to perform a universal or generic DELETE on a specified object under available
  Intersight API types, including those not yet defined in the Intersight SDK for Python. An argument for the
  API type path and MOID (managed object identifier) is required.
    
  Args:
    api_path: The path to the targeted Intersight API type. For example, to specify the Intersight API type for
      adapter configuration policies, enter "adapter/ConfigPolicies". More API types can be found in the Intersight
      API reference library at https://intersight.com/apidocs/introduction/overview/.
    moid: The managed object ID of the targeted API object.

  Returns:
    A statement indicating whether the DELETE method was successful or failed.
  
  Raises:
    Exception: An exception occured while performing the API call. The exact error will be
    specified.
  """
  full_resource_path = "/" + api_path + "/" + moid
  try:
    api_instance.call_api(full_resource_path,"DELETE")
    logging.info("The deletion of the object located at the resource path '" + full_resource_path + "' has been completed.")
    return "The DELETE method was successful."
  except Exception as exception_message:
    logging.info("Unable to access the object located at the resource path '" + full_resource_path + "'.")
    logging.info(exception_message)
    return "The DELETE method failed."


def iu_post(api_path,body):
  """This is a function to perform a universal or generic POST of an object under available Intersight
  API types, including those not yet defined in the Intersight SDK for Python. An argument for the
  API type path and body configuration data is required.
  
  Args:
    api_path: The path to the targeted Intersight API type. For example, to specify the Intersight API type for
      adapter configuration policies, enter "adapter/ConfigPolicies". More API types can be found in the Intersight
      API reference library at https://intersight.com/apidocs/introduction/overview/.
    body: The content to be created under the targeted API type. This should be provided in a dictionary format.
  
  Returns:
    A statement indicating whether the POST method was successful or failed.
    
  Raises:
    Exception: An exception occured while performing the API call. The exact error will be
    specified.
  """
  full_resource_path = "/" + api_path
  try:
    api_instance.call_api(full_resource_path,"POST",body=body)
    logging.info("The creation of the object under the resource path '" + full_resource_path + "' has been completed.")
    return "The POST method was successful."
  except Exception as exception_message:
    logging.info("Unable to create the object under the resource path '" + full_resource_path + "'.")
    logging.info(exception_message)
    return "The POST method failed."


def iu_post_moid(api_path,moid,body):
  """This is a function to perform a universal or generic POST of a specified object under available Intersight
  API types, including those not yet defined in the Intersight SDK for Python. An argument for the
  API type path, MOID (managed object identifier), and body configuration data is required.
      
  Args:
    api_path: The path to the targeted Intersight API type. For example, to specify the Intersight API type for
      adapter configuration policies, enter "adapter/ConfigPolicies". More API types can be found in the Intersight
      API reference library at https://intersight.com/apidocs/introduction/overview/.
    moid: The managed object ID of the targeted API object.
    body: The content to be modified on the targeted API object. This should be provided in a dictionary format.
  
  Returns:
    A statement indicating whether the POST method was successful or failed.
    
  Raises:
    Exception: An exception occured while performing the API call. The exact error will be
    specified.
  """
  full_resource_path = "/" + api_path + "/" + moid
  try:
    api_instance.call_api(full_resource_path,"POST",body=body)
    logging.info("The update of the object located at the resource path '" + full_resource_path + "' has been completed.")
    return "The POST method was successful."
  except Exception as exception_message:
    logging.info("Unable to access the object located at the resource path '" + full_resource_path + "'.")
    logging.info(exception_message)
    return "The POST method failed."


def iu_patch_moid(api_path,moid,body):
  """This is a function to perform a universal or generic PATCH of a specified object under available Intersight
  API types, including those not yet defined in the Intersight SDK for Python. An argument for the
  API type path, MOID (managed object identifier), and body configuration data is required.
      
  Args:
    api_path: The path to the targeted Intersight API type. For example, to specify the Intersight API type for
      adapter configuration policies, enter "adapter/ConfigPolicies". More API types can be found in the Intersight
      API reference library at https://intersight.com/apidocs/introduction/overview/.
    moid: The managed object ID of the targeted API object.
    body: The content to be modified on the targeted API object. This should be provided in a dictionary format.
  
  Returns:
    A statement indicating whether the PATCH method was successful or failed.
    
  Raises:
    Exception: An exception occured while performing the API call. The exact error will be
    specified.
  """
  full_resource_path = "/" + api_path + "/" + moid
  try:
    api_instance.call_api(full_resource_path,"PATCH",body=body)
    logging.info("The update of the object located at the resource path '" + full_resource_path + "' has been completed.")
    return "The PATCH method was successful."
  except Exception as exception_message:
    logging.info("Unable to access the object located at the resource path '" + full_resource_path + "'.")
    logging.info(exception_message)
    return "The PATCH method failed."


# Establish email alert functions and needed parameters
# Setup email alert sender and recipients
sender = "dCloud_DCV_Demos@dcloud.cisco.com"
receivers = ["uemekauw@cisco.com"]

# Setup email attachment files
session_xml_attachment = "c:\\dcloud\\session.xml"
cluster_xml_attachment = cluster_xml


def intersight_account_status_alert():
  """
  Function to alert for Intersight service account and API availability test errors
  """
  
  # Create Email
  msg = MIMEMultipart()
  msg["From"] = sender
  msg["To"] = ", ".join(receivers)
  msg["Date"] = formatdate(localtime=True)
  msg["Subject"] = "[dCloud Demo Service Account Alert]: Intersight Service Account " + intersight_account_name + " is Unavailable"

  # Email body content
  message = """<html>
  <body>
  <b>BRIEF SUMMARY ON AFFECTED SERVICE ACCOUNT:</b>
  <br>
  Service Account Type: %(intersight_account_service_type)s
  <br>
  Name: %(intersight_account_name)s
  <br>
  Email: %(intersight_account_email)s
  <br>
  Associated Cluster: %(intersight_account_cluster)s
  <br>
  Session ID: %(intersight_account_session)s
  <br>
  Location: %(intersight_account_location)s
  <br><br>

  <b>ISSUE:</b> Please be advised that on %(date)s, the Intersight service account named %(intersight_account_name)s did not pass the availability test for session ID #%(intersight_account_session)s located in %(intersight_account_location)s. Please directly check the Intersight service account at https://intersight.com to verify the account status and that all permitted users are present. See the attached session.xml and cluster.xml files for additional details on the demo session and Intersight service account.
  <br><br>

  <b>RESOLUTION:</b> Verify that the HyperFlex Edge cluster was actually assigned to the demo session, as the Intersight service account will not be assigned without a matching cluster. If the service account type, name, email, cluster and location in the above summary are blank, than likely an oversubscription of resources has occured on the dCloud platform. Other causes may be that an Intersight cloud service is down. Visit https://status.intersight.com to check the status of Intersight cloud services.
  </body>
  </html>

  <br><br>
  """ % dict(
    intersight_account_name=intersight_account_name,
    intersight_account_service_type=intersight_account_service_type,
    intersight_account_email=intersight_account_email,
    intersight_account_cluster=intersight_account_cluster,
    intersight_account_session=intersight_account_session,
    intersight_account_location=intersight_account_location,
    date=date
    )

  msg.attach(MIMEText(message, "html"))

  files = [session_xml_attachment, cluster_xml_attachment]

  for xml in files:
          attachment = open(xml, "rb")
          file_name = os.path.basename(xml)
          part = MIMEBase("application", "octet-stream")
          part.set_payload(attachment.read())
          part.add_header("Content-Disposition", "attachment", filename=file_name)
          encoders.encode_base64(part)
          msg.attach(part)

  try:
    # Set SMTP server and send email
    smtpserver = smtplib.SMTP("192.168.100.100")
    smtpserver.sendmail(sender, receivers, msg.as_string())
    smtpserver.quit()
    logging.info("A notification email was successfully sent for Intersight service account and API availability test errors.")
  except Exception:
    logging.info("Unable to reach the SMTP server at 192.168.100.100.")


# Establish function to test for the availability of the Intersight API and Intersight account

def test_intersight_service():
  """This is a function to test the availability of the Intersight API and Intersight account. The Intersight account
  tested for is the owner of the provided Intersight API key and key ID.
  """
  try:
    # Check that Intersight Account is accessible
    logging.info("Testing access to the Intersight API by verifying the Intersight account information...")
    check_account = intersight.IamAccountApi(api_instance)
    get_account = check_account.iam_accounts_get()
    if check_account.api_client.last_response.status is not 200:
      logging.info("The Intersight API and Account Availability Test did not pass.")
      logging.info("The Intersight account information could not be verified.")
      logging.info("Exiting due to the Intersight account being unavailable.\n")
      sys.exit(0)
    else:
      account_name = get_account.results[0].name
      logging.info("The Intersight API and Account Availability Test has passed.")
      logging.info("The Intersight account named '" + intersight_account_name + "' has been found.")
  except Exception:
    logging.info("Unable to access the Intersight API.")
    logging.info("Exiting due to the Intersight API being unavailable.\n")
    sys.exit(0)


# Run the Intersight API and Account Availability Test
logging.info("Running the Intersight API and Account Availability Test.")
test_intersight_service()

# Create the HyperFlex Local Credential Policy for the Cluster Configuration "Security" policy type settings
local_credential_api_path = "hyperflex/LocalCredentialPolicies"
local_credential_api_body = {
  "Name": "sample-local-credential-policy",
  "Description": "A sample Local Credential Policy for the dCloud HyperFlex Edge demo.",
  "FactoryHypervisorPassword": True,
  "HypervisorAdmin": "root",
  "HypervisorAdminPwd": "C1sco12345!",
  "HxdpRootPwd": "C1sco12345!"
}
iu_post(local_credential_api_path, local_credential_api_body)

# Create the HyperFlex System Configuration Policy for the Cluster Configuration "DNS, NTP, and Timezone" policy type settings
system_configuration_api_path = "hyperflex/SysConfigPolicies"
system_configuration_api_body = {
  "Name": "sample-sys-config-policy",
  "Description": "A sample System Configuration Policy for the dCloud HyperFlex Edge demo.",
  "DnsDomainName": "dcloud.cisco.com",
  "DnsServers": ["192.168.100.100"],
  "NtpServers": ["198.18.128.1"],
  "Timezone": "America/New_York"
}
iu_post(system_configuration_api_path, system_configuration_api_body)

# Create the HyperFlex VMware vCenter Configuration Policy for the Cluster Configuration "vCenter (Optional)" policy type settings
vcenter_configuration_api_path = "hyperflex/VcenterConfigPolicies"
vcenter_configuration_api_body = {
  "Name": "sample-vcenter-config-policy",
  "Description": "A sample VMware vCenter Configuration Policy for the dCloud HyperFlex Edge demo.",
  "DataCenter": "dCloud-DC",
  "Hostname": "198.18.133.30",
  "Username": "administrator@vsphere.local",
  "Password": "C1sco12345!"
}
iu_post(vcenter_configuration_api_path, vcenter_configuration_api_body)

# Create the HyperFlex Cluster Storage Configuration Policy for the Cluster Configuration "Storage Configuration (Optional)" policy type settings
cluster_storage_api_path = "hyperflex/ClusterStoragePolicies"
cluster_storage_api_body = {
  "Name": "sample-cluster-storage-policy",
  "Description": "A sample Cluster Storage Configuration Policy for the dCloud HyperFlex Edge demo.",
  "DiskPartitionCleanup": True,
  "VdiOptimization": False
}
iu_post(cluster_storage_api_path, cluster_storage_api_body)

# Create the HyperFlex Node Configuration Policy for the Cluster Configuration "IP & Hostname" policy type settings
node_configuration_api_path = "hyperflex/NodeConfigPolicies"
node_configuration_api_body = {
  "Name": "sample-node-config-policy",
  "Description": "A sample Node Configuration Policy for the dCloud HyperFlex Edge demo.",
  "NodeNamePrefix": "hx-edge-esxi",
  "MgmtIpRange": {
    "EndAddr": "198.18.135.102",
    "Gateway": "198.18.128.1",
    "Netmask": "255.255.192.0",
    "ObjectType": "hyperflex.IpAddrRange",
    "StartAddr": "198.18.135.101"
  },
  "HxdpIpRange": {
    "EndAddr": "198.18.135.104",
    "Gateway": "198.18.128.1",
    "Netmask": "255.255.192.0",
    "ObjectType": "hyperflex.IpAddrRange",
    "StartAddr": "198.18.135.103"
  },
}
iu_post(node_configuration_api_path, node_configuration_api_body)

# Create the HyperFlex Cluster Network Configuration Policy for the Cluster Configuration "Network Configuration" policy type settings
cluster_network_api_path = "hyperflex/ClusterNetworkPolicies"
cluster_network_api_body = {
  "Name": "sample-cluster-network-policy",
  "Description": "A sample Cluster Network Configuration Policy for the dCloud HyperFlex Edge demo.",
  "MgmtVlan": {
    "VlanId": 0
  },
  "UplinkSpeed": "10G",
  "JumboFrame": False,
  "MacPrefixRange": {
    "EndAddr": "00:25:B5:00",
    "ObjectType": "hyperflex.MacAddrPrefixRange",
    "StartAddr": "00:25:B5:00"
  },
}
iu_post(cluster_network_api_path, cluster_network_api_body)

# Intersight HyperFlex policy creation complete
logging.info("The Intersight Policy Set Creator for HyperFlex Edge Script is complete.\n")

# Exiting Intersight HyperFlex Policy Creator
sys.exit(0)
