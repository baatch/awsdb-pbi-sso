# Power BI on AWS Databricks using SSO Passthrough
This repo contains the notebook and Power BI template that can be used together to demo SSO passthrough for Power BI connecting to AWS Databricks. AWS Databricks customers who are using Azure Active Directory (Entra ID) as Oauth mechanism can leverage this SSO passthrough feature. SSO passthorugh will allow you to leverage Unity Catalog Access Control instead of setting up seperate access control in Power BI. 

### Youtube Video on Demo
[![How to use SSO passthrough for power bi connecting to AWS Databricks](https://img.youtube.com/vi/IZPrUTO1dqU/0.jpg)](https://www.youtube.com/watch?v=IZPrUTO1dqU)

## Prerequisites
In order to use SSO passthrough for AWS Databricks customers who are using Entra ID as Oauth mechanism, you will need to
* Do self-enrollment for this private preview feature  https://docs.databricks.com/en/integrations/configure-aad-sso-powerbi.html
* Use Azure Databricks Connector, watch the below video for the difference between different Databricks connectors in Power BI
  
[![Databricks connectors on Power BI](https://img.youtube.com/vi/YQU5TfgJMzs/0.jpg)](https://www.youtube.com/watch?v=YQU5TfgJMzs)
* Use **Direct Query** Storage Mode for Power BI Semantic Model on top of Databricks

## How to set up
### Notebook setup
* Populate the catalog and schema in widgets
* Assign different users to different groups outlined in the notebook "ap_demo_admin" and "ap_demo_fr"
* run notebook
  
### Use the Demo Template File
Open the .PBIT file downloaded from this github repo, populate below parameters:
Server_Hostname (From your SQL warehouse connection strings)
HTTP_Path (From your SQL warehouse connection strings)
Catalog_Name (What you defined in the RLS notebook)
Schema_Name (What you defined in the RLS notebook)
