
// :snippet-start: threads-list-traces-basic-after-go
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
	minStart, _ := time.Parse(time.RFC3339, "2026-07-01T00:00:00Z")
	maxStart, _ := time.Parse(time.RFC3339, "2026-07-31T23:59:59Z")
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
		Selects:   langsmith.F([]langsmith.ThreadListTracesParamsSelect{langsmith.ThreadListTracesParamsSelectStartTime}),
	})
	for iter.Next() {
		trace := iter.Current()
		fmt.Println(trace.TraceID, trace.StartTime)
		// :remove-start:
		break
		// :remove-end:
	}
	if err := iter.Err(); err != nil {
		panic(err.Error())
	}
}
// :snippet-end:
