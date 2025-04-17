# media-polarisation

This project aims to measure the bias from different media outlets in their articles and the topics they mention in them. This project is created with the main purpose of helping people who regularly view the news and want to understand how polarised and biased different news outlets are on important and overarching topics like "Donald Trump" or "Amazon". However, there are many more user groups which could potentially use this project.

![Architecture-diagram](/architecture/cloud_architecture.png)
**Fig 1**: Cloud architecture diagram for the project.

![ERD-diagram](/architecture/schema/ERD.png)
**Fig 2**: Cloud architecture diagram for the project.

**Fig 1** shows the cloud architecture diagram used. The central part of the architecture is the RDS used on AWS. This database used PostgresSQL. The ERD for the database is shown in **Fig 2**, which was what the schema was based off. The four boxes indicate the four main sections of the architecture:
- Scraper pipeline
- Archival pipeline
- Emailing service
- Dashboard service

## Directory Structure

### **1. Architecture**

The [`architecture`](architecture/) directory contains Terraform scripts to provision AWS resources (such as the Lambda's, RDS and S3) and also includes the ERD and cloud architecture diagrams. All cloud resources in this project were provisioned using Terraform to ensure the cloud resources are reliable and re-deployable.
For details, see [Architecture README](architecture/README.md).

---

### **2. Scraper pipeline**

The [scraper pipeline](/scraper-pipeline/) contains the code to define the two lambda handlers used for this pipeline. The first is the dispatcher Lambda, which is triggered by an event scheduler. This then further triggers the worker Lambdas, one for each media outlet, which complete the ETL process and inserts the analysis into the remote RDS.
For details, see [Scraper pipeline README](scraper-pipeline/README.md).

---

### **3. Archival pipeline**

The [archival pipeline](/archival-pipeline/) contains the code to define the Lambda function used in archival pipeline. The goal is to archive data older than three months into a CSV on the S3 bucket which is a more cost-effective and long term storage solution in comparison to the RDS.
For details, see [Archival pipeline README](archival-pipeline/README.md).

---

### **4. Daily report**

The [daily report](/daily-report/) contains the code to define the Lambda functiona used in the Emailing service. It utilises AWS's Simple Email Service (SES) to send emails to subscribed users. These emails contain a PDF attachment of the daily report which contains summary and analytics from the previous day.
For details, see [Daily report README](daily-report/README.md).

---

### **5. Dashboard**

The [dashboard](/dashboard/) contains the code to define the streamlit dashboard which contains graphs and statistics derived from the data in the RDS.
For details, see [Dashboard README](dashboard/README.md).

---

## User Stories

As a person who values reading unbiased news, I want to be able to see evidence of political bias amongst news outlets, so that I can better extract the truth from what I'm reading.

As a busy person, I want to receive a daily report containing trending topics from the day so that I can stay on top of global news.

As a general user, I want to receive a daily report summarising which topics are most divisive in opinion between news outlets to better understand possible biases.

As a general user, I want to receive a daily report with key headlines from the previous day, so that I can easily stay on top of global news.

As a person with a certain political leaning, I want to be able to choose news outlets which correspond with my political beliefs in order to see news which aligns with my beliefs.

As a person with a certain political leaning, I want to able to choose news outlets which oppose my political beliefs in order to challenge my beliefs and expand my knowledge.

As a person who values reading unbiased news, I want to be able to see the bias the the ways news outlets address specific topics in order to highlight their political leanings.

As a general user, I want to view sentiment trends over time for a topic across multiple sources so that I can identify shifts in media tone.

As a general user, I want to use the dashboard to visualise the difference in sentiment for different news outlets, to best understand the trends.

As a general user, I want to have access to links which direct me to articles, so that I can actually read the articles which are being compared.

As a researcher, I want to download coverage data for a topic over time so that I can conduct my own analysis. 

As an admin, I want to monitor the health of the data pipeline so that I can ensure article ingestion is running smoothly.

As an admin, I want to monitor the health of the data pipeline so that I can ensure article ingestion is running smoothly.

As an admin, I want to run tests which ensure the pipelines are working as expected.