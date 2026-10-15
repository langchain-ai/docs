
// :snippet-start: runs-query-list-root-as-traces-before-go
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

	rootRuns, err := client.Runs.Query(ctx, langsmith.RunQueryParams{
		Session: langsmith.F([]string{projectID}),
		IsRoot:  langsmith.F(true),
		Limit:   langsmith.F(int64(5)),
	})
	if err != nil {
		panic(err.Error())
	}
	for _, run := range rootRuns.Runs {
		fmt.Println(run.TraceID, run.Name)
	}
}
// :snippet-end:
