// :remove-start:
console.log("✓ multimodal summarization illustration validated");
process.exit(0);
// :remove-end:

// :snippet-start: multimodal-summarization-js
// Before — model receives image blocks in older turns
void {
  role: "user",
  content: [
    { type: "text", text: "What trends do you see in this chart?" },
    { type: "image", url: "https://example.com/chart.png" },
  ],
};
void {
  role: "tool",
  content: [
    { type: "text", text: "Updated chart:" },
    { type: "image", url: "https://example.com/chart-v2.png" },
  ],
};

// After — those turns collapse to text; image blocks are gone
void {
  content:
    "User asked about trends in a chart screenshot. " +
    "Tool returned an updated chart. Agent identified Q3 revenue growth.",
};
// :snippet-end:
