---
title: Oracle Autonomous Database
---

Oracle Autonomous Database is a cloud database that uses machine learning to automate database tuning, security, backups, updates, and other routine management tasks traditionally performed by DBAs.

This notebook covers how to load documents from Oracle Autonomous Database, the loader supports connection with connection string or tns configuration.

## Prerequisites

1. Install `python-oracledb`: `pip install oracledb`
   1. See [Installing `python-oracledb`](https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html).

## Instructions

```python
pip install oracledb
```

```python
from langchain_community.document_loaders import OracleAutonomousDatabaseLoader
from settings import s
```

With mutual TLS authentication (mTLS), wallet_location and wallet_password parameters are required to create the connection. See python-oracledb documentation [Connecting to Oracle Cloud Autonomous Databases](https://python-oracledb.readthedocs.io/en/latest/user_guide/connection_handling.html#connecting-to-oracle-cloud-autonomous-databases).

```python
SQL_QUERY = "select prod_id, time_id from sh.costs fetch first 5 rows only"

doc_loader_1 = OracleAutonomousDatabaseLoader(
    query=SQL_QUERY,
    user=s.USERNAME,
    password=s.PASSWORD,
    schema=s.SCHEMA,
    config_dir=s.CONFIG_DIR,
    wallet_location=s.WALLET_LOCATION,
    wallet_password=s.PASSWORD,
    tns_name=s.TNS_NAME,
)
doc_1 = doc_loader_1.load()

doc_loader_2 = OracleAutonomousDatabaseLoader(
    query=SQL_QUERY,
    user=s.USERNAME,
    password=s.PASSWORD,
    schema=s.SCHEMA,
    connection_string=s.CONNECTION_STRING,
    wallet_location=s.WALLET_LOCATION,
    wallet_password=s.PASSWORD,
)
doc_2 = doc_loader_2.load()
```

With 1-way TLS authentication, only the database credentials and connection string are required to establish a connection. The example below also shows passing bind variable values with the argument `parameters`.

```python
SQL_QUERY = "select channel_id, channel_desc from sh.channels where channel_desc = :1 fetch first 5 rows only"

doc_loader_3 = OracleAutonomousDatabaseLoader(
    query=SQL_QUERY,
    user=s.USERNAME,
    password=s.PASSWORD,
    schema=s.SCHEMA,
    config_dir=s.CONFIG_DIR,
    tns_name=s.TNS_NAME,
    parameters=["Direct Sales"],
)
doc_3 = doc_loader_3.load()

doc_loader_4 = OracleAutonomousDatabaseLoader(
    query=SQL_QUERY,
    user=s.USERNAME,
    password=s.PASSWORD,
    schema=s.SCHEMA,
    connection_string=s.CONNECTION_STRING,
    parameters=["Direct Sales"],
)
doc_4 = doc_loader_4.load()
```
