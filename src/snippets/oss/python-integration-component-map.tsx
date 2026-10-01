type Component = {
  id: string;
  label: string;
  href: string;
};

const retrievalFlow: Component[] = [
  { id: "document-loaders", label: "Document loaders", href: "/oss/integrations/document_loaders" },
  { id: "splitters", label: "Text splitters", href: "/oss/integrations/splitters" },
  { id: "embeddings", label: "Embedding models", href: "/oss/integrations/embeddings" },
  { id: "vectorstores", label: "Vector stores", href: "/oss/integrations/vectorstores" },
  { id: "retrievers", label: "Retrievers", href: "/oss/integrations/retrievers" },
  { id: "chat", label: "Chat models", href: "/oss/integrations/chat" },
];

const agentComponents: Component[] = [
  { id: "tools", label: "Tools", href: "/oss/integrations/tools" },
  { id: "middleware", label: "Middleware", href: "/oss/integrations/middleware" },
];

const executionAndStateComponents: Component[] = [
  { id: "sandboxes", label: "Sandboxes", href: "/oss/integrations/sandboxes" },
  { id: "backends", label: "Backends", href: "/oss/integrations/backends" },
  { id: "checkpointers", label: "Checkpointers", href: "/oss/integrations/checkpointers" },
  { id: "long-term-memory", label: "Long-term memory", href: "/oss/integrations/long-term-memory" },
];

function ComponentLink({ component, active }: { component: Component; active: string }) {
  const isCurrent = component.id === active;
  return (
    <a
      href={component.href}
      aria-current={isCurrent ? "page" : undefined}
      className={`rounded-md border px-3 py-2 text-center text-sm font-medium no-underline transition-colors ${
        isCurrent
          ? "border-[#006DDD] bg-[#E5F4FF] text-[#030710] ring-2 ring-[#006DDD] dark:border-[#7FC8FF] dark:bg-[#161F34] dark:text-[#F2FAFF] dark:ring-[#7FC8FF]"
          : "border-[#40668D] bg-[#F2FAFF] text-[#030710] hover:border-[#006DDD] dark:border-[#40668D] dark:bg-[#0D1322] dark:text-[#F2FAFF] dark:hover:border-[#7FC8FF]"
      }`}
    >
      {component.label}
      {isCurrent && <span className="sr-only"> (current page)</span>}
    </a>
  );
}

export default function PythonIntegrationComponentMap({ active }: { active: string }) {
  return (
    <figure aria-labelledby="python-integration-component-map-title" className="not-prose my-6 rounded-xl border border-[#40668D] bg-[#F2FAFF] p-4 dark:border-[#40668D] dark:bg-[#0D1322] sm:p-5">
      <figcaption id="python-integration-component-map-title" className="mb-4 text-sm font-semibold text-[#030710] dark:text-[#F2FAFF]">
        Integration components
        <span className="ml-2 font-normal text-[#2F4B68] dark:text-[#99D3FF]">Arrows show a typical retrieval flow. The outlined component is this page.</span>
      </figcaption>
      <section aria-label="Typical retrieval flow" className="rounded-lg border border-[#40668D] bg-[#E5F4FF] p-3 dark:border-[#40668D] dark:bg-[#161F34]">
        <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-[#2F4B68] dark:text-[#99D3FF]">Typical retrieval flow</h3>
        <div className="flex flex-wrap items-center justify-center gap-2">
          {retrievalFlow.map((component, index) => (
            <div key={component.id} className="flex items-center gap-2">
              <ComponentLink component={component} active={active} />
              {index < retrievalFlow.length - 1 && <span aria-hidden="true" className="text-[#40668D] dark:text-[#99D3FF]">→</span>}
            </div>
          ))}
        </div>
      </section>
      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <section aria-label="Agent capabilities" className="rounded-lg border border-[#40668D] bg-[#E5F4FF] p-3 dark:border-[#40668D] dark:bg-[#161F34]">
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-[#2F4B68] dark:text-[#99D3FF]">Agent capabilities</h3>
          <div className="grid gap-2 sm:grid-cols-2">
            {agentComponents.map((component) => <ComponentLink key={component.id} component={component} active={active} />)}
          </div>
        </section>
        <section aria-label="Execution and state" className="rounded-lg border border-[#40668D] bg-[#E5F4FF] p-3 dark:border-[#40668D] dark:bg-[#161F34]">
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-[#2F4B68] dark:text-[#99D3FF]">Execution and state</h3>
          <div className="grid gap-2 sm:grid-cols-2">
            {executionAndStateComponents.map((component) => <ComponentLink key={component.id} component={component} active={active} />)}
          </div>
        </section>
      </div>
    </figure>
  );
}
