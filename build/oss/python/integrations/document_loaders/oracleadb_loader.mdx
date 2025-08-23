---
title: Oracle Autonomous Database
---

Oracle autonomous database is a cloud database that uses machine learning to automate database tuning, security, backups, updates, and other routine management tasks traditionally performed by DBAs.

This notebook covers how to load documents from oracle autonomous database, the loader supports connection with connection string or tns configuration.

## Prerequisites
1. Database runs in a 'Thin' mode:
   https://python-oracledb.readthedocs.io/en/latest/user_guide/appendix_b.html
2. `pip install oracledb`:
   https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html

## Instructions


```python
pip install oracledb
```


```python
from langchain_community.document_loaders import OracleAutonomousDatabaseLoader
from settings import s
```

With mutual TLS authentication (mTLS), wallet_location and wallet_password are required to create the connection, user can create connection by providing either connection string or tns configuration details.


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

With TLS authentication, wallet_location and wallet_password are not required.
Bind variable option is provided by argument "parameters".


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
