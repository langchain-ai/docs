---
title: How to Deploy Self-Hosted Data Plane
---
Before deploying, review the [conceptual guide for the Self-Hosted Data Plane](langgraph_self_hosted_data_plane) deployment option.

<Info>
  **Important**
  The Self-Hosted Data Plane deployment option is currently in beta stage and requires an [Enterprise](plans) plan.
</Info>

## Prerequisites

1. Use the [LangGraph CLI](langgraph_cli) to [test your application locally](local-server).
2. Use the [LangGraph CLI](langgraph_cli) to build a Docker image (i.e. `langgraph build`) and push it to a registry your Kubernetes cluster or Amazon ECS cluster has access to.

## Kubernetes

### Prerequisites

1. `KEDA` is installed on your cluster.
  helm repo add kedacore https://kedacore.github.io/charts
  helm install keda kedacore/keda --namespace keda --create-namespace
2. A valid `Ingress` controller is installed on your cluster.
3. You have slack space in your cluster for multiple deployments. `Cluster-Autoscaler` is recommended to automatically provision new nodes.

### Setup

1. You give us your LangSmith organization ID. We will enable the Self-Hosted Data Plane for your organization.
2. We provide you a [Helm chart](https://github.com/langchain-ai/helm/tree/main/charts/langgraph-dataplane) which you run to setup your Kubernetes cluster. This chart contains a few important components.
  1. `langgraph-listener`: This is a service that listens to LangChain's [control plane](langgraph_control_plane) for changes to your deployments and creates/updates downstream CRDs.
  2. `LangGraphPlatform CRD`: A CRD for LangGraph Platform deployments. This contains the spec for managing an instance of a LangGraph Platform deployment.
  3. `langgraph-platform-operator`: This operator handles changes to your LangGraph Platform CRDs.
3. Configure your `langgraph-dataplane-values.yaml` file.
  config:
  langgraphPlatformLicenseKey: "" # Your LangGraph Platform license key
  langsmithApiKey: "" # API Key of your Workspace
  langsmithWorkspaceId: "" # Workspace ID
  hostBackendUrl: "https://api.host.langchain.com" # Only override this if on EU
  smithBackendUrl: "https://api.smith.langchain.com" # Only override this if on EU
4. Deploy `langgraph-dataplane` Helm chart.
  helm repo add langchain https://langchain-ai.github.io/helm/
  helm repo update
  helm upgrade -i langgraph-dataplane langchain/langgraph-dataplane --values langgraph-dataplane-values.yaml
5. If successful, you will see two services start up in your namespace.
  NAME                                          READY   STATUS              RESTARTS   AGE
  langgraph-dataplane-listener-7fccd788-wn2dx   0/1     Running             0          9s
  langgraph-dataplane-redis-0                   0/1     ContainerCreating   0          9s
6. You create a deployment from the [control plane UI](langgraph_control_plane#control-plane-ui).

## Amazon ECS

Coming soon!
