
// :snippet-start: traces-list-runs-basic-before-go
// :codegroup-tab: Before
package main

import (
	"context"
	"fmt"

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

	runs, err := client.Runs.Query(ctx, langsmith.RunQueryParams{
		Session: langsmith.F([]string{projectID}),
		Trace:   langsmith.F(traceID),
	})
	if err != nil {
		panic(err.Error())
	}
	for _, run := range runs.Runs {
		fmt.Println(run.Name, run.RunType, run.Status)
	}
}
// :snippet-end:
