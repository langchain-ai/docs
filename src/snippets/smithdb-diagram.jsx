export const SmithDBDiagram = ({ name }) => {
  const diagrams = {
    overview: {
      viewBox: "0 0 1380 1050",
      sources: {
        light: "/images/langsmith/smithdb/overview.svg",
        dark: "/images/langsmith/smithdb/overview-dark.svg",
      },
      title: "SmithDB and LangSmith architecture",
      description: "LangSmith services and SmithDB services, the dependencies between them, and their storage.",
    },
    "write-path": {
      viewBox: "0 0 1380 340",
      sources: {
        light: "/images/langsmith/smithdb/write-path.svg",
        dark: "/images/langsmith/smithdb/write-path-dark.svg",
      },
      title: "SmithDB write path",
      description: "The platform backend adds a task to Redis. An ingest queue worker writes the runs to SmithDB ingestion, which writes segments to object storage and segment rows to the metastore, then acknowledges the write.",
    },
    "read-path": {
      viewBox: "0 0 1380 360",
      sources: {
        light: "/images/langsmith/smithdb/read-path.svg",
        dark: "/images/langsmith/smithdb/read-path-dark.svg",
      },
      title: "SmithDB read path",
      description: "The platform backend queries SmithDB query, which reads the segment list from the metastore and segments from its disk cache, object storage, or the ingestion pod that wrote them.",
    },
    "feedback-path": {
      viewBox: "0 0 1380 400",
      sources: {
        light: "/images/langsmith/smithdb/feedback-path.svg",
        dark: "/images/langsmith/smithdb/feedback-path-dark.svg",
      },
      title: "SmithDB feedback path",
      description: "The platform backend adds feedback to the Redis feedback queue. An ingest queue worker sends it to the SmithDB mutations pool, which stores it in the metastore. Compaction later writes it to object storage.",
    },
  };

  const diagram = diagrams[name];

  return (
    <div className="smithdb-diagram-container">
      {["light", "dark"].map((theme) => {
        const source = diagram.sources[theme];
        return (
          <a
            key={theme}
            className="smithdb-diagram-link"
            data-diagram-theme={theme}
            href={source}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={`${diagram.title}: open full-size diagram`}
          >
            <svg
              className="smithdb-diagram"
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
