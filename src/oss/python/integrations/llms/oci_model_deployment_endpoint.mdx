---
title: OCI Data Science Model Deployment Endpoint
---

[OCI Data Science](https://docs.oracle.com/en-us/iaas/data-science/using/home.htm) is a fully managed and serverless platform for data science teams to build, train, and manage machine learning models in the Oracle Cloud Infrastructure.

> For the latest updates, examples and experimental features, please see [ADS LangChain Integration](https://accelerated-data-science.readthedocs.io/en/latest/user_guide/large_language_model/langchain_models.html).

This notebooks goes over how to use an LLM hosted on a [OCI Data Science Model Deployment](https://docs.oracle.com/en-us/iaas/data-science/using/model-dep-about.htm).

For authentication, the [oracle-ads](https://accelerated-data-science.readthedocs.io/en/latest/user_guide/cli/authentication.html) library is used to automatically load credentials required for invoking the endpoint.

```python
!pip3 install oracle-ads
```

## Prerequisite

### Deploy model

You can easily deploy, fine-tune, and evaluate foundation models using the [AI Quick Actions](https://docs.oracle.com/en-us/iaas/data-science/using/ai-quick-actions.htm) on OCI Data Science Model deployment. For additional deployment examples, please visit the [Oracle GitHub samples repository](https://github.com/oracle-samples/oci-data-science-ai-samples/blob/main/ai-quick-actions/llama3-with-smc.md).

### Policies

Make sure to have the required [policies](https://docs.oracle.com/en-us/iaas/data-science/using/model-dep-policies-auth.htm#model_dep_policies_auth__predict-endpoint) to access the OCI Data Science Model Deployment endpoint.

## Set up

After having deployed model, you have to set up following required parameters of the call:

- **`endpoint`**: The model HTTP endpoint from the deployed model, e.g. `https://modeldeployment.<region>.oci.customer-oci.com/<md_ocid>/predict`.

### Authentication

You can set authentication through either ads or environment variables. When you are working in OCI Data Science Notebook Session, you can leverage resource principal to access other OCI resources. Check out [here](https://accelerated-data-science.readthedocs.io/en/latest/user_guide/cli/authentication.html) to see more options.

## Examples

```python
import ads
from langchain_community.llms import OCIModelDeploymentLLM

# Set authentication through ads
# Use resource principal are operating within a
# OCI service that has resource principal based
# authentication configured
ads.set_auth("resource_principal")

# Create an instance of OCI Model Deployment Endpoint
# Replace the endpoint uri and model name with your own
# Using generic class as entry point, you will be able
# to pass model parameters through model_kwargs during
# instantiation.
llm = OCIModelDeploymentLLM(
    endpoint="https://modeldeployment.<region>.oci.customer-oci.com/<md_ocid>/predict",
    model="odsc-llm",
)

# Run the LLM
llm.invoke("Who is the first president of United States?")
```

```python
import ads
from langchain_community.llms import OCIModelDeploymentVLLM

# Set authentication through ads
# Use resource principal are operating within a
# OCI service that has resource principal based
# authentication configured
ads.set_auth("resource_principal")

# Create an instance of OCI Model Deployment Endpoint
# Replace the endpoint uri and model name with your own
# Using framework specific class as entry point, you will
# be able to pass model parameters in constructor.
llm = OCIModelDeploymentVLLM(
    endpoint="https://modeldeployment.<region>.oci.customer-oci.com/<md_ocid>/predict",
)

# Run the LLM
llm.invoke("Who is the first president of United States?")
```

```python
import os

from langchain_community.llms import OCIModelDeploymentTGI

# Set authentication through environment variables
# Use API Key setup when you are working from a local
# workstation or on platform which does not support
# resource principals.
os.environ["OCI_IAM_TYPE"] = "api_key"
os.environ["OCI_CONFIG_PROFILE"] = "default"
os.environ["OCI_CONFIG_LOCATION"] = "~/.oci"

# Set endpoint through environment variables
# Replace the endpoint uri with your own
os.environ["OCI_LLM_ENDPOINT"] = (
    "https://modeldeployment.<region>.oci.customer-oci.com/<md_ocid>/predict"
)

# Create an instance of OCI Model Deployment Endpoint
# Using framework specific class as entry point, you will
# be able to pass model parameters in constructor.
llm = OCIModelDeploymentTGI()

# Run the LLM
llm.invoke("Who is the first president of United States?")
```

### Asynchronous calls

```python
await llm.ainvoke("Tell me a joke.")
```

### Streaming calls

```python
for chunk in llm.stream("Tell me a joke."):
    print(chunk, end="", flush=True)
```

## API reference

For comprehensive details on all features and configurations, please refer to the API reference documentation for each class:

- [OCIModelDeploymentLLM](https://python.langchain.com/api_reference/community/llms/langchain_community.llms.oci_data_science_model_deployment_endpoint.OCIModelDeploymentLLM.html)
- [OCIModelDeploymentVLLM](https://python.langchain.com/api_reference/community/llms/langchain_community.llms.oci_data_science_model_deployment_endpoint.OCIModelDeploymentVLLM.html)
- [OCIModelDeploymentTGI](https://python.langchain.com/api_reference/community/llms/langchain_community.llms.oci_data_science_model_deployment_endpoint.OCIModelDeploymentTGI.html)
