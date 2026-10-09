export const SandboxDiagram = ({ name }) => {
  const diagrams = {
    architecture: {
      viewBox: "0 0 900 730",
      sources: {
        light: "/images/langsmith/sandboxes/self-host-architecture.svg",
        dark: "/images/langsmith/sandboxes/self-host-architecture-dark.svg",
      },
      title: "Self-hosted Sandbox architecture",
      description: "Apps connect to the platform backend, which manages sandbox hosts on dedicated Kubernetes nodes. PostgreSQL stores placement, while JuiceFS uses dedicated Redis metadata and object storage.",
    },
    node: {
      viewBox: "0 0 820 630",
      sources: {
        light: "/images/langsmith/sandboxes/self-host-node.svg",
        dark: "/images/langsmith/sandboxes/self-host-node-dark.svg",
      },
      title: "Inside one sandbox node",
      description: "One privileged sandbox-host pod manages multiple Firecracker microVMs with separate kernels and guest agents. KVM and a disposable cache are local; JuiceFS connects to shared storage outside the node.",
    },
    autoscaling: {
      viewBox: "0 0 820 470",
      sources: {
        light: "/images/langsmith/sandboxes/self-host-autoscaling.svg",
        dark: "/images/langsmith/sandboxes/self-host-autoscaling-dark.svg",
      },
      title: "Two layers of Sandbox autoscaling",
      description: "Hosts report committed CPU through Leases. An elected host scales the Deployment, and the node autoscaler provides eligible nodes. New hosts check storage before accepting placements.",
    },
    "scaling-behavior": {
      viewBox: "0 0 820 400",
      sources: {
        light: "/images/langsmith/sandboxes/self-host-scaling-behavior.svg",
        dark: "/images/langsmith/sandboxes/self-host-scaling-behavior-dark.svg",
      },
      title: "Sandbox scaling behavior",
      description: "A qualitative chart shows ready hosts lagging behind rising demand. After demand falls, the replica target holds its peak for a stabilization window, then decreases gradually.",
    },
    rollout: {
      viewBox: "0 0 820 430",
      sources: {
        light: "/images/langsmith/sandboxes/self-host-rollout.svg",
        dark: "/images/langsmith/sandboxes/self-host-rollout-dark.svg",
      },
      title: "One-host-at-a-time rolling upgrade",
      description: "Four hosts drain and start a new version sequentially. An otherwise healthy pool has three hosts ready during each replacement, and all four ready when the rollout finishes.",
    },
  };

  if (!Object.hasOwn(diagrams, name)) {
    throw new Error("Unknown Sandbox diagram");
  }

  const diagram = diagrams[name];

  return (
    <div className="sandbox-diagram-container">
      {["light", "dark"].map((theme) => {
        const source = diagram.sources[theme];
        return (
          <a
            key={theme}
            className="sandbox-diagram-link"
            data-diagram-theme={theme}
            href={source}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={`${diagram.title}: open full-size diagram`}
          >
            <svg
              className="sandbox-diagram"
              viewBox={diagram.viewBox}
              role="img"
              aria-label={diagram.description}
              focusable="false"
            >
              <use href={`${source}#diagram`} />
            </svg>
          </a>
        );
      })}
    </div>
  );
};
