# Contributing to LangChain Docs

Please read our [contributing guide](https://docs.langchain.com/oss/python/contributing/overview) to learn how you can make a contribution to the LangChain ecosystem and documentation.

Happy writing!
🎤🦜

## Update the egress IP inventory

Edit [the shared inventory](../src/langsmith/egress-ip-addresses.json), which generates the LangSmith and LangSmith Deployment IP tables.

Each address has a service (`langsmith` or `langsmith-deployment`), cloud (`gcp` or `aws`), customer region (`us`, `eu`, or `apac`), IPv4 `/32` CIDR, and status.
Use `reserved` for allocated addresses that are not attached, and `active` for addresses already in use.
Customers must allowlist both statuses. Publish new reserves before using them, and mark consumed reserves `active`.
Remove an address only after it stops carrying traffic and has been released.

From the repository root, regenerate and verify the inventory version and both tables:

```sh
python scripts/generate_egress_ip_tables.py
python scripts/generate_egress_ip_tables.py --check
```

Commit the JSON and generated page changes together. Do not edit the generated tables or `version` by hand.
After deployment, verify the changes in [the public JSON](https://docs.langchain.com/langsmith/egress-ip-addresses.json).
