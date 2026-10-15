
// :snippet-start: traces-list-runs-filter-before-go
// :codegroup-tab: Before
package main

import (
	"context"

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
	rootRuns, err := client.Runs.Query(ctx, langsmith.RunQueryParams{
		Session: langsmith.F([]string{projectID}),
		IsRoot:  langsmith.F(true),
		Limit:   langsmith.F(int64(1)),
	})
	if err != nil {
		panic(err.Error())
	}
	traceID = rootRuns.Runs[0].TraceID
	// :remove-end:

	_, err = client.Runs.Query(ctx, langsmith.RunQueryParams{
		Session: langsmith.F([]string{projectID}),
		Trace:   langsmith.F(traceID),
		Filter:  langsmith.F(`eq(run_type, "llm")`),
	})
	if err != nil {
		panic(err.Error())
	}
}
// :snippet-end:
