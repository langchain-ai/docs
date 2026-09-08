
// :snippet-start: runs-query-list-root-as-traces-after-go
// :codegroup-tab: After
package main

import (
	"context"
	"fmt"
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

	maxStart := time.Now().UTC()
	minStart := maxStart.AddDate(0, -1, 0)

	iter := client.Traces.QueryAutoPaging(ctx, langsmith.TraceQueryParams{
		ProjectID:    langsmith.F(projectID),
		MinStartTime: langsmith.F(minStart),
		MaxStartTime: langsmith.F(maxStart),
		Selects:      langsmith.F([]langsmith.RunSelectField{langsmith.RunSelectFieldName}),
	})
	count := 0
	for iter.Next() {
		trace := iter.Current()
		fmt.Println(trace.RootRun.TraceID, trace.RootRun.Name)
		count++
		if count >= 5 {
			break
		}
	}
	if err := iter.Err(); err != nil {
		panic(err.Error())
	}
}
// :snippet-end:
