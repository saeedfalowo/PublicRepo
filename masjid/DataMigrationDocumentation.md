# Data Migration
This documentation entails all steps involved in migrating .xlsx or .xls excel file data to remote postgresql database along with all the queries required to view and filter the data.

This documentation will provide information on how to convert data files like this:
![Raw Excel File](images/raw_excel_screenshot.png)


To something that looks like this:
```
select * from sample_insurance_tbl
```
![Raw SQL Table](images/raw_dbeaver_table_screenshot.png)


And operations like these could be performed for further data analysis:
```
select location, count(*) as cnt from sample_insurance_tbl group by location order by cnt desc;
```
![Location count](images/sql_location_count.png)

```
select region, count(*) cnt from sample_insurance_tbl group by region order by cnt asc;
```
![Region count](images/sql_region_count.png)

```
select businesstype, count(*) cnt from sample_insurance_tbl group by 1 order by 2 desc;
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

Double click on the Idon to Launch `DBeaver` SQL client application.
![DBeaver Desktop Icon](images/dbeaver_application.png)

## 3 - Setup Remote PostgreSQL Database
