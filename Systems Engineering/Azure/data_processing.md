---
created: 2025-11-02 07:47:38
---
## Data factory
>[!note] Azure Data Factory is, in essence, a lightweight data orchestration tool.

>**Azure Data Factory (ADF)** is Microsoft's cloud-based ETL (Extract, Transform, Load) and data integration service designed to orchestrate and automate data movement and transformation at scale. 

- ADF can be used to create, manage, and schedule data **pipelines**.

>A **pipeline** is a logical grouping of activities that together perform a task.

>An **activity** defines a specific task or action performed within a pipeline, such as moving or transforming data.

>[!example] ADF is commonly used, for example, for moving data from on-premises to cloud.


- Simply speaking, Data Factory is a cloud data integration service used to create automated pipelines for data storage, movement, and processing services.  

Azure Data Factory consists of six key components that work together:

- **Pipelines**
	-  
	- Pipelines are used to manage activities as a set rather than individually; activities in a pipeline can run sequentially or in parallel.
	- For example, a pipeline might contain activities that extract data from an SQL database, transform it, and then load it into a data warehouse.

- **Activities**
	- **Activities** define the actions performed on your data. 
	- Azure Data Factory supports two main types of activities:
		- **Data movement activities** (copying data between sources).
		- **Data transformation activities** (modifying, cleaning, or enriching data).

- **Datasets**
	- **Datasets** represent data structures within data stores. 
	- An input dataset provides data to an activity, while an output dataset receives the result.
	- For example, an Azure Blob dataset specifies which blob container and folder to read from, or an Azure SQL table dataset defines where to write output data.

- **Linked Services**
	- **Linked Services** define connection information for Azure Data Factory to connect to external resources. Similar to connection strings, they specify how to connect to databases, storage accounts, or other services. 
	- For example, an Azure Storage linked service contains credentials and connection details for your storage account.

- **Data Flows**
	- **Mapping Data Flows** provide you with a graphical interface you can use to design data transformation logic. 
	- ADF executes these transformations on Spark clusters that automatically scale up when needed and shut down when complete, so you don't have to manage infrastructure yourself.

- **Integration Runtimes**
	- **Integration Runtimes** provide the compute infrastructure where activities execute. They bridge between your data sources and Azure Data Factory, so that ADF can connect to both cloud and on-premises resources.


```
inc3311198
```