# Databricks notebook source
# MAGIC %md
# MAGIC # 🛡️ AWS Databricks + Power BI SSO
# MAGIC <img src="https://github.com/dbalexp/aws-db-uc-pbi-sso/blob/main/doc/title_logo.png?raw=true" width="400" style="float: right; margin-top: 20; margin-right: 20" alt="A"/>
# MAGIC
# MAGIC In this demo, you'll learn how to use AWS Databricks and Power BI SSO to harness the power of Unity Catalog to secure your data at a more granular level using its *row-level* and *column-level* access control capabilities.

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC # Prerequisties
# MAGIC Make sure all the prerequities on the infrastructure side have been completed
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC # Review demo customers table

# COMMAND ----------

# DBTITLE 1,Set catalog to users and schema to alexander_phu
# MAGIC %sql
# MAGIC USE CATALOG ${catalog};
# MAGIC USE SCHEMA ${schema};

# COMMAND ----------

# DBTITLE 1,Querying All Records from the Customers Table
# MAGIC %sql
# MAGIC -- Query the customers table
# MAGIC SELECT * FROM customers;

# COMMAND ----------

# DBTITLE 1,Counting the Number of Rows in the Customers Table
# MAGIC %sql
# MAGIC -- Query row count on customers table (68879)
# MAGIC SELECT COUNT(*) FROM customers;

# COMMAND ----------

# DBTITLE 1,Distinct Country Values from Customers Table
# MAGIC %sql
# MAGIC
# MAGIC -- Query distinct country values from the customers table (3)
# MAGIC SELECT DISTINCT(country) FROM customers;

# COMMAND ----------

# MAGIC %md
# MAGIC # Switch to Power BI
# MAGIC
# MAGIC <img src="https://github.com/dbalexp/aws-db-uc-pbi-sso/blob/main/doc/title_logo.png?raw=true" width="400" style="float: right; margin-top: 20; margin-right: 20" alt="A"/>
# MAGIC
# MAGIC
# MAGIC
# MAGIC ## Option 1
# MAGIC - Switch to Power BI Desktop, Use the downloaded Power BI template file from the repo 
# MAGIC - Fill in the parameters for catalog, schema, sql warehouse settings
# MAGIC
# MAGIC
# MAGIC
# MAGIC ## Option 2
# MAGIC - Switch to Power BI Desktop and create a report using the Azure Databricks Connector.
# MAGIC - Sign in with Azure AD option and select Direct Query option.
# MAGIC - Select the customers table
# MAGIC - Build some visuals
# MAGIC - Save the report, and Publish to Power BI Service. 
# MAGIC
# MAGIC
# MAGIC
# MAGIC
# MAGIC
# MAGIC
# MAGIC
# MAGIC
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## [Check Power BI Report](https://app.powerbi.com/groups/ac0fa11c-fc3a-43f9-9873-fe62816f439d/reports/8d5eb330-a831-4190-9789-000deeb66b94/ReportSection?experience=power-bi)

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC # Set fine grained access control (RLS & CLS)
# MAGIC Back in Databricks, let's define some fine grained access control like row level security and column level security

# COMMAND ----------

# DBTITLE 1,Verify Group Membership
# MAGIC %sql
# MAGIC -- Test if the current user is a member of the 'ap_demo_admin' group and 'ap_demo_fr' group
# MAGIC SELECT current_user(), 'ap_demo_admin' as group_name, is_account_group_member('ap_demo_admin')
# MAGIC UNION ALL
# MAGIC SELECT current_user(), 'ap_demo_fr' as group_name, is_account_group_member('ap_demo_fr')
# MAGIC ;
# MAGIC

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC
# MAGIC ## Row level access control 
# MAGIC
# MAGIC <img src="https://github.com/databricks-demos/dbdemos-resources/blob/main/images/product/uc/acls/table_uc_rls.png?raw=true" width="200" style="float: right; margin-top: 20; margin-right: 20" alt="databricks-demos"/>
# MAGIC
# MAGIC Row-level security allows you to automatically hide a subset of your rows based on who is attempting to query it, without having to maintain any seperate copies of your data.
# MAGIC
# MAGIC A typical use-case would be to filter out rows based on your country or Business Unit : you only see the data (financial transactions, orders, customer information...) pertaining to your region, thus preventing you from having access to the entire dataset.
# MAGIC
# MAGIC 💡 While this filter can be applied at the user / principal level, it is recommended to implement access policies using groups instead.
# MAGIC <br style="clear: both"/>
# MAGIC
# MAGIC
# MAGIC
# MAGIC
# MAGIC
# MAGIC

# COMMAND ----------

# DBTITLE 1,Create Region Filter Function
# MAGIC %sql
# MAGIC
# MAGIC -- Create new row filter function
# MAGIC CREATE OR REPLACE FUNCTION region_filter_fr(region_param STRING) 
# MAGIC RETURN 
# MAGIC   is_account_group_member('ap_demo_admin') OR  -- Admin can access all regions
# MAGIC   region_param LIKE "FR%";                     -- Non-admins can only access regions containing 'FR'
# MAGIC
# MAGIC -- Grant access to all users to the function for the demo by making all account users owners
# MAGIC GRANT ALL PRIVILEGES ON FUNCTION region_filter_fr TO `account users`;

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Test Function region_filter_fr. 
# MAGIC -- As expected, FR return true and USA returns false
# MAGIC SELECT region_filter_fr('USA'), region_filter_fr('FR')
# MAGIC
# MAGIC

# COMMAND ----------

# DBTITLE 1,Set Row Filter Function on Table
# MAGIC %sql
# MAGIC
# MAGIC -- Set a row filter function on the 'customers' table to restrict access based on the 'country' column
# MAGIC ALTER TABLE customers SET ROW FILTER region_filter_fr ON (country);

# COMMAND ----------

# MAGIC %md
# MAGIC <img src="https://github.com/databricks-demos/dbdemos-resources/blob/main/images/product/uc/acls/table_uc_cls.png?raw=true" width="200" style="float: right; margin-top: 20; margin-right: 20; margin-left: 20" alt="databricks-demos"/>
# MAGIC
# MAGIC ## Column Level access control (Optional)
# MAGIC
# MAGIC Similarly, column-level access control helps you mask or anonymise the data that is in certain columns of your table, depending on the user or service principal that is trying to access it. This is typically used to mask or remove sensitive PII informations from your end users (email, SSN...).

# COMMAND ----------

# DBTITLE 1,Create Simple Mask Function
# MAGIC %sql
# MAGIC -- Create a SQL function for a simple column mask
# MAGIC CREATE OR REPLACE FUNCTION simple_mask(column_value STRING)
# MAGIC RETURN 
# MAGIC   IF(is_account_group_member('ap_demo_admin'), column_value, "****");
# MAGIC
# MAGIC -- Grant all privileges on the function to account users (only for demo purposes)
# MAGIC GRANT ALL PRIVILEGES ON FUNCTION simple_mask TO `account users`; -- only for demo, don't do that in prod as everybody could change the function

# COMMAND ----------

# DBTITLE 1,Simple Address Masking
# MAGIC %sql
# MAGIC -- Applying our simple masking function to the 'address' column in the 'customers' table
# MAGIC ALTER TABLE
# MAGIC   customers
# MAGIC ALTER COLUMN
# MAGIC   address
# MAGIC SET
# MAGIC   MASK simple_mask;

# COMMAND ----------

# MAGIC %md 
# MAGIC
# MAGIC ## Query table in Databricks to verify if RLS and CLS are applied

# COMMAND ----------

# DBTITLE 1,Query the Customers table
# MAGIC %sql
# MAGIC -- Query the customers table (verify CLS on column adress)
# MAGIC SELECT * FROM customers;
# MAGIC

# COMMAND ----------

# DBTITLE 1,Table Row Count SQL Query
# MAGIC %sql
# MAGIC -- Query the total number of rows in the customers table (23119)
# MAGIC SELECT count(*) FROM customers;

# COMMAND ----------

# DBTITLE 1,Distinct Country Name
# MAGIC %sql
# MAGIC
# MAGIC -- Query distinct country values from the customers table (1)
# MAGIC SELECT DISTINCT(country) FROM customers;
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC # Switch to Power BI Service
# MAGIC
# MAGIC <img src="https://github.com/dbalexp/aws-db-uc-pbi-sso/blob/main/doc/title_logo.png?raw=true" width="400" style="float: right; margin-top: 20; margin-right: 20" alt="A"/>
# MAGIC
# MAGIC - Switch to Power BI Service and refresh the Power BI report. 
# MAGIC - Verify that RLS and CLS has kicked in
# MAGIC
# MAGIC
# MAGIC
# MAGIC
# MAGIC
# MAGIC

# COMMAND ----------

# MAGIC %md 
# MAGIC
# MAGIC ## Check Databricks Query History
# MAGIC Switch to the Query History tab to verify the queries being run on the SQL Warehouse from the Power BI Service

# COMMAND ----------

# MAGIC %md
# MAGIC
# MAGIC ## Remove RLS and CLS
# MAGIC

# COMMAND ----------

# DBTITLE 1,Remove Row Filter from Customers Table
# MAGIC %sql
# MAGIC -- Remove row filter on the 'customers' table
# MAGIC ALTER TABLE customers DROP ROW FILTER;

# COMMAND ----------

# DBTITLE 1,Removing column mask on address
# MAGIC %sql
# MAGIC -- Removing the column mask on 'address' from the 'customers' table
# MAGIC ALTER TABLE customers ALTER COLUMN address DROP MASK;
