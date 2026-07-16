
// :snippet-start: traces-query-totals-after-go
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

	minStart, _ := time.Parse(time.RFC3339, "2026-07-01T00:00:00Z")
	maxStart, _ := time.Parse(time.RFC3339, "2026-07-31T23:59:59Z")

	iter := client.Traces.QueryAutoPaging(ctx, langsmith.TraceQueryParams{
		ProjectID:    langsmith.F(projectID),
		MinStartTime: langsmith.F(minStart),
		MaxStartTime: langsmith.F(maxStart),
		Selects: langsmith.F([]langsmith.TraceQueryParamsSelect{
			langsmith.TraceQueryParamsSelectName,
			langsmith.TraceQueryParamsSelectTotalTokens,
			langsmith.TraceQueryParamsSelectTotalCost,
		}),
	})
	count := 0
	for iter.Next() {
		trace := iter.Current()
		count++
		if trace.TraceAggregates.JSON.RawJSON() != "" {
			fmt.Println(trace.RootRun.Name, trace.TraceAggregates.TotalTokens, trace.TraceAggregates.TotalCost)
		}
		if count >= 5 {
			break
		}
	}
	if err := iter.Err(); err != nil {
		panic(err.Error())
	}
}
// :snippet-end:
