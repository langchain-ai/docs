
// :snippet-start: threads-list-traces-selecting-fields-after-go
// :codegroup-tab: After
package main

import (
	"context"
	"fmt"
	"time"

	"github.com/langchain-ai/langsmith-go"
)

// :remove-start:
func findThreadID(ctx context.Context, client *langsmith.Client, projectID string) string {
	maxStart := time.Now().UTC()
	minStart := maxStart.AddDate(0, -1, 0)
	iter := client.Threads.QueryAutoPaging(ctx, langsmith.ThreadQueryParams{
		ProjectID:    langsmith.F(projectID),
		MinStartTime: langsmith.F(minStart),
		MaxStartTime: langsmith.F(maxStart),
	})
	if iter.Next() {
		return iter.Current().ThreadID
	}
	panic("no threads found")
}
// :remove-end:
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
	threadID := "<thread-id>"
	// :remove-start:
	threadID = findThreadID(ctx, client, projectID)
	// :remove-end:

	iter := client.Threads.ListTracesAutoPaging(ctx, threadID, langsmith.ThreadListTracesParams{
		ProjectID: langsmith.F(projectID),
		Selects: langsmith.F([]langsmith.ThreadListTracesParamsSelect{
			langsmith.ThreadListTracesParamsSelectTraceID,
			langsmith.ThreadListTracesParamsSelectTotalTokens,
			langsmith.ThreadListTracesParamsSelectTotalCost,
		}),
	})
	for iter.Next() {
		trace := iter.Current()
		fmt.Println(trace.TraceID, trace.TotalTokens, trace.TotalCost)
		// :remove-start:
		break
		// :remove-end:
	}
	if err := iter.Err(); err != nil {
		panic(err.Error())
	}
}
// :snippet-end:
