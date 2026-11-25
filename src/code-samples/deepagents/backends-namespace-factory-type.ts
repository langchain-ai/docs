// :snippet-start: backends-namespace-factory-type-js
type StoreBackendNamespaceFactory = (context: {
  state: unknown;
  config?: {
    metadata?: Record<string, unknown>;
    configurable?: Record<string, unknown>;
  };
  assistantId?: string;
}) => string[];
// :snippet-end:

// :remove-start:
const factory: StoreBackendNamespaceFactory = ({ assistantId }) => [
  assistantId ?? "filesystem",
];
if (factory({ state: {} }).length === 0) {
  throw new Error("expected namespace components");
}
console.log("✓ backends-namespace-factory-type validated");
// :remove-end:
