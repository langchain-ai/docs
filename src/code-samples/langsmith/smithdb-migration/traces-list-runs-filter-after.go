
// :snippet-start: traces-list-runs-filter-after-go
// :codegroup-tab: After
package main

import (
	"context"
	"time"

	"github.com/langchain-ai/langsmith-go"
)

func main() {
	ctx := context.Background()
	client := langsmith.NewClient()

	sessions, err := client.Sessions.List(ctx, langsmith.SessionListParams{
		Name:  langsmith.F("default"),
		Limit: langsmith.F(int64(1)),
	})
	if err != nil {
		panic(err.Error())
	}
	projectID := sessions.Items[0].ID
	traceID := "<trace-id>"
	// :remove-start:
	minStart, _ := time.Parse(time.RFC3339, "2026-07-01T00:00:00Z")
	maxStart, _ := time.Parse(time.RFC3339, "2026-07-31T23:59:59Z")
	iter := client.Traces.QueryAutoPaging(ctx, langsmith.TraceQueryParams{
		ProjectID:    langsmith.F(projectID),
		MinStartTime: langsmith.F(minStart),
		MaxStartTime: langsmith.F(maxStart),
	})
	if iter.Next() {
		traceID = iter.Current().RootRun.TraceID
	}
	// :remove-end:

	_, err = client.Traces.ListRuns(ctx, traceID, langsmith.TraceListRunsParams{
		ProjectID: langsmith.F(projectID),
		Filter:    langsmith.F(`eq(run_type, "llm")`),
		Selects: langsmith.F([]langsmith.TraceListRunsParamsSelect{
			langsmith.TraceListRunsParamsSelectName,
			langsmith.TraceListRunsParamsSelectStatus,
		}),
	})
	if err != nil {
		panic(err.Error())
	}
}
// :snippet-end:
