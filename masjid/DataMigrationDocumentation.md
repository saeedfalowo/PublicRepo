# Data Migration
This documentation entails all steps involved in migrating .xlsx or .xls excel file data to remote postgresql database along with all the queries required to view and filter the data.

This documentation will provide information on how to convert data files like this:

![Raw Excel File](images/raw_excel_screenshot.png)


To something that looks like this:
```
select * from loaded.insurance_raw
```

![Raw SQL Table](images/raw_dbeaver_table_screenshot.png)


And operations like these could be performed for further data analysis:
```
select location, count(*) as cnt from loaded.insurance_raw group by location order by cnt desc;
```

![Location count](images/sql_location_count.png)

```
select region, count(*) cnt from loaded.insurance_raw group by region order by cnt asc;
```

![Region count](images/sql_region_count.png)

```
select businesstype, count(*) cnt from loaded.insurance_raw group by 1 order by 2 desc;
```

![BusinessType count](images/sql_businesstype_count.png)

And many more operations can be done on the data to reveal new insights hiding therein.

## 1 - Preparing the data files for ingestion
Excel files with .xls or xlsx file extensions are not friendly enough for raw data extraction due to their nested nature (as in having multiple pages within). Therefore the data within each of those pages in the excel file needs to be extracted into csv files.

The following two .xlsx files without macros have been downloaded as test files to work on from [Excel Sample Data](https://www.contextures.com/xlsampledata01.html).

![Sample Files](images/sample_files_screenshot.png)

This portion of the documentation will use the `SampleData_Insurance.xlsx` file.

To export the datafile as a csv file, all that is needed is to save file file as a csv file while on the data page in the excel file.

![Data Page](images/excel_data_page_screenshot.png)

In this `SampleData_Insurance.xlsx` file, the highlighted `PolicyData` page is the data page that needs to be exported.

![File Tab](images/fileTabResponse_in_excel.png)

Under the underlined File tab, the highlighted `Save As` button can be seen and once clicked...

![Save As CSV](images/excel_save_as_csv_event.png)

The file name and path can be changed as desired but the `Save as type` must be changed to CSV (Comma delimited) (*.csv) as highlighted. And then click the `Save` button.

![Save As CSV](images/excel_save_as_csv_event_2.png)

Click `OK` or `Yes` at the event of the following prompts:

![Save Event Prompt 1](images/excel_save_as_csv_event_prompt.png)

![Save Event Prompt 2](images/excel_save_as_csv_event_prompt_2.png)

Now close the excel window and click `Don't Save` at this prompt:

![Close Event Prompt](images/excel_close_csv_event_prompt.png)

We should now have the exported csv file in our taget location.

![Sample .xlsx and Exported .csv file](images/sample_files_and_generated_csv_file_screenshot.png)

Now we need to open the csv file as raw text without any of excel's formating.

Right click on the file to show the `Open with` option

![Open with Event](images/open_with_event.png).

Under `Open with` select `Notepad` if available, otherwise, select `Choose another app` and choose `Notepad` and select `Just once` (Recommended) or `Always`.

![Open with Event](images/open_with_event_2.png).

The file should look like this in its raw form:

![Raw Exported CSV Text](images/raw_csv_text_screenshot.png)

Now, this is a much easier data file to work with.

Repeat this for all the data files you have to prepare each of them for migration.


## 2 - Installing SQL Client Application
There are a multitude of free SQL Client Applications available online, and almost any of them can be used in for this migration task, however, [DBeaver](https://dbeaver.io) is the application being used for this task. Navigate to the DBeaver website, `https://dbeaver.io`, or search DBeaver on google and navigate to their home page.

![DBeaver Home](images/dbeaver_home.png)

Click the download button to navigate to the download page.

![DBeaver Download Page](images/dbeaver_download.png)

The host system for this migration uses a Window's Operating System so the `Windows (Installer)` version was clicked and downloaded. Choose your appropriate operating system installer.

![DBeaver Installer](images/dbeaver_installer.png)

Once the installer has been downloaded, double click on it to install the application.

Click the higlighted/pointed out options for all following prompts...

![DBeaver Installer prompt 1](images/dbeaver_installer_prompt_1.png)

![DBeaver Installer prompt 2](images/dbeaver_installer_prompt_2.png)

![DBeaver Installer prompt 3](images/dbeaver_installer_prompt_3.png)

![DBeaver Installer prompt 4](images/dbeaver_installer_prompt_4.png)

![DBeaver Installer prompt 5](images/dbeaver_installer_prompt_5.png)

![DBeaver Installer prompt 6](images/dbeaver_installer_prompt_6.png)

![DBeaver Installer prompt 7](images/dbeaver_installer_prompt_7.png)

We should then see this icon on the desktop and in `Start`.

![DBeaver Desktop Icon](images/dbeaver_desktop_icon.png)

Double click on the Icon to Launch `DBeaver` SQL client application.

![DBeaver Desktop Icon](images/dbeaver_application.png)

## 3 - Setup Remote PostgreSQL Database
Structured Query Language (SQL) storing and processing structured tabular data in a relational database. A relational database stores information in tabular form, with rows and columns representing different data attributes and the various relationships between the data values.

PostgreSQl is one of the most widely used SQL flavours. This migration task will be making use of PostgreSQL.

There are a few remote PostgreSQl clusters providers that provides various levels for free-tier compute plans.

[ElephantSQL](https://www.elephantsql.com/plans.html) have about 20MB free-tier memory limit.

However, the provider that will be used for this migration is the [Neon](https://neon.tech/pricing) compute provider with their 3GB* free-tier memory limit.

`*` 3GB per branch and Neon allows for 10 branches in its free-tier plan.

### 3.1 - Registering and Setting up PostgreSQL cluster on Neon
Navigate to the [Neon](https://neon.tech) website, https://neon.tech, from your browser.

![Neon Home Page](images/neon_home.png)

Click the `Sign up` button if you dont have an account already, or click `Sign In` if you do.

![Neon Sign Up Page](images/neon_signup_page.png)

On the `Sign Up` page, click `Continue with Google` if you have a google account or click `Continue with Github` if you have a Github account.

Upon clicking the `Continue with Google` button, you should see a page where you will need to sign into your google email account, if none of your google accounts is currently signed into on your browser, like this:

![Google Account Sign In](images/neon_signup_with_google_account_sign_in.png)

Or you will get a page with all your current active google accounts to choose from, like this:

![Active Google Account Options](images/neon_signup_with_google_accounts_options.png)

After registration, you should now see the projects page...

![Neon Projects Page](images/neon_projects_page.png)

Click `Create a project` and enter the desired project name, and change Region to Europe if you reside in Europe, or other region that is closest to you. Leave other options as default then click `Create project`.

![Neon Create Project Prompt](images/neon_create_project_prompt.png)

A prompt for the newly created project connection details will pop up.

![Neon Project Connection Details](images/neon_project_connection_details_prompt.png)

Highlights
- Yellow: **Username**
- Teal (Blue): **Password**
- Orange: **Host**
- Purple: **Database**

Close the prompt and you will be taken to the Dashboard page...

![Neon Dashboard Page](images/neon_dashboard_page.png)

Click the `Skip` button to close the `Neon onboarding` info banner.

![Neon Dashboard Page](images/neon_dashboard_2_page.png)

You can also see the postgresql connection details examples by clicking the underlined `connection examples` link (not actual connection details for the project, just an example).

You can also create a new database from the `Connection Details` box...

![Neon Connection Details Box](images/neon_connection_details.png)

![Neon Create Database Prompt](images/neon_create_database_prompt.png)

![Neon Connection Details Box](images/neon_connection_details_2.png)

You can then copy the connection string for either of the databases by first unmasking the password portion of the string or just directly using the copy button on the right of the string box to copy the connection string.

![Neon Connection Details Box](images/neon_connection_details_3.png)

![Neon Connection Details Box](images/neon_connection_details_4.png)

- **neondb** connection string: `postgres://tyslogo:Go6cKQkmbOl8@ep-curly-limit-741542.eu-central-1.aws.neon.tech/neondb`
  - Username: `tyslogo`
  - Password: `Go6cKQkmbOl8`
  - Host: `ep-curly-limit-741542.eu-central-1.aws.neon.tech`
  - Database: `neondb`
- **main_db** connection string: `postgres://tyslogo:Go6cKQkmbOl8@ep-curly-limit-741542.eu-central-1.aws.neon.tech/main_db`
  - Username: `tyslogo`
  - Password: `Go6cKQkmbOl8`
  - Host: `ep-curly-limit-741542.eu-central-1.aws.neon.tech`
  - Database: `main_db`


### 3.2 - Connecting DBeaver to Neon PostgreSQL Cluster
Open up the DBeaver application...

![DBeaver Application](images/dbeaver_application_2.png)

Click on the `New Database Connection` Icon on the top left corner of the DBeaver window.

Choose the `PostgreSQL` option on the `All` tab and click `Next`.

![Select your database](images/dbeaver_connect_to_database_1.png)

Configure the postgreSQL database with the connection string given on the Neon Dashboard and partitioned into different fields as done in the previous section:

- **neondb** connection string: `postgres://tyslogo:Go6cKQkmbOl8@ep-curly-limit-741542.eu-central-1.aws.neon.tech/neondb`
  - Username: `tyslogo`
  - Password: `Go6cKQkmbOl8`
  - Host: `ep-curly-limit-741542.eu-central-1.aws.neon.tech`
  - Database: `neondb`

And leave the Port number as the default: 5432.

![Configure PostgreSQL Database](images/dbeaver_connect_to_database_2.png)

Test the connection with the `Test Connection ...` button.

![Test PostgreSQL Database Connection](images/dbeaver_connect_to_database_3.png)

Click the `OK` button and then the `Finish` button if the Connection Test proves successful.

![Connect to PostgreSQL Database](images/dbeaver_connect_to_database_4.png)

Click the `Database Navigator` button on the top left on the DBeaver application. Select the desired database from the list and click the `Connect` plug icon &#128268; to connect to the database.

![View New PostgreSQL Database](images/dbeaver_connect_to_database_5.png)

Upon successful connection, the connected database will gain a green tick.

![View New PostgreSQL Database](images/dbeaver_connect_to_database_6.png)

Click the `Open SQL script` option in the SQL button dropdown to open a new SQL script.

### 3.3 - Migrate CSV file data into SQL table
There are multiple ways to partition SQL data to keep data separate. Three of these are using Databases (as we have two databases `neondb` and `main_db`), Schemas, and Tables.

![Database Tree](images/dbeaver_queries_1.png)

Only the default `public` schema can be seen in the Database tree. Let's create a `loaded` schema to hold our raw tables.

Write the sql statement below and click the &#9654;, play, button to execute the query.
```
create schema loaded;
```

![Create Schema](images/dbeaver_queries_0.png)

This query will create a new schema called `loaded`. However, to see the new schema in the database tree, the tree needs to be refreshed first. Right click on the `neondb` connection and click `Refresh` in the dropdown.

![Refresh Connection](images/dbeaver_queries_2.png)

![View Schema](images/dbeaver_queries_3.png)

Now we need to create a table for our CSV files data within the `loaded` schema.

Open the previously exported CSV file with Notepad as formally described.

![CSV file header](images/csv_file_header.png)

Copy the header (column name line) of the csv file and construct the `Create Table` statement like so:

```
create table loaded.insurance_raw (
	policy			text,
	expiry			text,
	location		text,
	state			text,
	region			text,
	insuredValue 	text,
	construction 	text,
	businessType 	text,
	earthquake 		text,
	flood 			text
);
```

Use the `Tab` keyboard key to align the column names and their datatypes (not required, a single white space between the column names and their datatypes will do).

![Create Table Statement](images/dbeaver_create_table.png)

Place the cursor at the last line of the query after the semicolon, `;`, make sure all the underlined spots have the target database named there, and then press the &#9654;, play, button to execute the `Create table` statement.

Refresh the connection to see the newly created table under the database tree.
![Create Table Statement](images/dbeaver_create_table_2.png)

Query the new table to see the contents of the table.

```
select * from loaded.insurance_raw;
```

![Create Table Statement](images/dbeaver_create_table_3.png)

Should show an empty table.

Now we need to insert the csv data file contents into the new table.

Click on the &#128268;+ icon to create a new connection.

![DBeaver Application](images/dbeaver_application_2.png)

Search for within the `All` tab, select the `CSV` connection and click `Next >`

![Create CSV Connection](images/dbeaver_csv_connection_1.png)

![Create CSV Connection](images/dbeaver_csv_connection_2.png)

![Create CSV Connection](images/dbeaver_csv_connection_3.png)

Choose your desired folder to use as your csv database. The example uses exported csv file folder as the csv database folder.

![Create CSV Connection](images/dbeaver_csv_connection_4.png)

After clicking the `Finish` button, navigate to the database tree and right-click on the desired empty table and click `Import Data` to import the csv file data into the table.

![Create CSV Connection](images/dbeaver_csv_connection_5.png)

![Create CSV Connection](images/dbeaver_csv_connection_6.png)

Select the export csv file.

![Create CSV Connection](images/dbeaver_csv_connection_7.png)

![Create CSV Connection](images/dbeaver_csv_connection_8.png)

![Create CSV Connection](images/dbeaver_csv_connection_9.png)

![Create CSV Connection](images/dbeaver_csv_connection_10.png)

![Create CSV Connection](images/dbeaver_csv_connection_11.png)

![Create CSV Connection](images/dbeaver_csv_connection_12.png)

Upon loading the csv file contents into the table, query the table again to confirm that data has been imported successfully.

```
select * from loaded.insurance_raw;
```

![Query CSV Data in Table](images/dbeaver_csv_connection_13.png)

### 3.4 - Create View from table for analysis
Cast columns (`expiry` and `insuredvalue`) to appropriate datatypes in a view without touching the original raw table.

```
drop view if exists loaded.insurance_vw;
create or replace view loaded.insurance_vw as
	select
		policy,
		to_date(expiry, 'DD-MON-YY') as expiry,
		location,
		state,
		region,
		replace(insuredValue, ',', '')::numeric insuredvalue,
		construction,
		businessType,
		earthquake,
		flood
	from loaded.insurance_raw
;
```

![View Result](images/dbeaver_view_query.png)

- Which businessType appeared the most in any given month of the year. Which Year-Month? And how many times?
  - ```
    select left(expiry::varchar, 7) year_month, businessType, count(*)
    from loaded.insurance_vw
    group by 1, 2 order by 3 desc;
    ```
  - ![Answer](images/dbeaver_view_analysis_1.png)
- Which businessType does not appeared at least once in any month of the year within the table.
  - ```
    with unq_months as (
        select distinct left(expiry::varchar, 7) year_month
        from loaded.insurance_vw
    ), num_months as (
        select count(*) from unq_months
    ), unq_months_businessType as (
        select distinct left(expiry::varchar, 7) year_month, businessType
        from loaded.insurance_vw
    )
    select businessType, count(*) cnt from unq_months_businessType
    group by 1
    having count(*) < (select * from num_months)
    order by 2 desc;
    ```
  - ![Answer](images/dbeaver_view_analysis_2.png)
- Which businessType does not appeared at least once in any month of the year.
  - ```
    with unq_months_businessType as (
        select distinct left(expiry::varchar, 7) year_month, businessType
        from loaded.insurance_vw
    )
    select businessType, count(*) cnt from unq_months_businessType
    group by 1
    having count(*) < 12
    order by 2 desc;
    ```
  - ![Answer](images/dbeaver_view_analysis_3.png)

### 3.5 - Insert, Update, Delete from raw table
New rows can be added, existing rows can be altered/updated, and deleted in the table (not view).

All or specific columns can be inserted during the insert operation.

Before insert:

```
select * from loaded.insurance_vw
where policy = '000000';
```

![Query for 000000 Policy](images/dbeaver_insert_delete_1.png)

```
insert into loaded.insurance_raw (policy, insuredValue)
values ('000000', '123');
```

![Insert 1 row](images/dbeaver_insert_delete_2.png)

After insert:

```
select * from loaded.insurance_vw
where policy = '000000';
```

![Query for 000000 Policy](images/dbeaver_insert_delete_3.png)

Delete from raw table:

```
delete from loaded.insurance_raw
where policy = '000000';
```

![Delete 000000 Policy](images/dbeaver_insert_delete_4.png)

```
select * from loaded.insurance_vw
where policy = '000000';
```

![Query for 000000 Policy](images/dbeaver_insert_delete_1.png)

Insert multiple rows:

```
insert into loaded.insurance_raw (policy, insuredValue)
values ('000000', '123'),
		('000000', '456');
```
![Insert 2 rows](images/dbeaver_insert_delete_5.png)

After insert:

```
select * from loaded.insurance_vw
where policy = '000000';
```

![Query for 000000 Policy](images/dbeaver_insert_delete_6.png)

Update raw table:

Out of all two rows with the same policy id, update just one using multiple filters.

```
update loaded.insurance_raw
set location = 'London'
where policy = '000000' and insuredValue = '456;
```

![Update rows with multiple filters](images/dbeaver_insert_delete_7.png)

![Update rows with multiple filters](images/dbeaver_insert_delete_8.png)

Update all rows with a single policy id:

```
update loaded.insurance_raw
set businesstype = 'Religious Services'
where policy = '000000';
```

![Update rows with single filter](images/dbeaver_insert_delete_9.png)

![Update rows with single filter](images/dbeaver_insert_delete_10.png)

### 3.6 - Export Tables, Views, or Query Results as CSV Files

![Export Table as CSV](images/dbeaver_export_as_csv_1.png)

![Export Table as CSV](images/dbeaver_export_as_csv_2.png)

![Export Table as CSV](images/dbeaver_export_as_csv_3.png)

![Export Table as CSV](images/dbeaver_export_as_csv_4.png)

![Export Table as CSV](images/dbeaver_export_as_csv_5.png)

![Export Table as CSV](images/dbeaver_export_as_csv_6.png)

![Export Table as CSV](images/dbeaver_export_as_csv_7.png)

![Export Table as CSV](images/dbeaver_export_as_csv_8.png)

The same process can be followed to export Views into csv files.

![Export View as CSV](images/dbeaver_export_as_csv_9.png)

![Export View as CSV](images/dbeaver_export_as_csv_10.png)

![Export View as CSV](images/dbeaver_export_as_csv_11.png)

Exporting Query results also follows the same process with some differences...

Starts from clicking the `Export data` drop down while in the query result tab to be exported.

![Export Query Results as CSV](images/dbeaver_export_as_csv_12.png)

![Export Query Results as CSV](images/dbeaver_export_as_csv_13.png)

![Export Query Results as CSV](images/dbeaver_export_as_csv_14.png)

The rest of the steps are identical to what were mentioned in the previous steps for exporting tables and views into csv files.

![Export Query Results as CSV](images/dbeaver_export_as_csv_15.png)

![Export Query Results as CSV](images/dbeaver_export_as_csv_16.png)

![Export Query Results as CSV](images/dbeaver_export_as_csv_17.png)

### 3.7 - Joins
Joins in SQL is a way to merge multiple tables together to extend the range of information. There are a multitude of ways to merge tables and views together, here is a youtube video showcasing some of the major join methods.

[SQL Joins Explained |¦| Joins in SQL |¦| SQL Tutorial](https://www.youtube.com/watch?v=9yeOJ0ZMUYw)


## 4 - REF
[1] - https://www.postgresql.org/docs/8.1/functions-formatting.html