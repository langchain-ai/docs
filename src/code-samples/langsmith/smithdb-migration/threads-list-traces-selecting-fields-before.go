
// :snippet-start: threads-list-traces-selecting-fields-before-go
// :codegroup-tab: Before
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

	runs, err := client.Runs.Query(ctx, langsmith.RunQueryParams{
		Session: langsmith.F([]string{projectID}),
		IsRoot:  langsmith.F(true),
		Filter:  langsmith.F(fmt.Sprintf(`eq(thread_id, "%s")`, threadID)),
		Select: langsmith.F([]langsmith.RunQueryParamsSelect{
			langsmith.RunQueryParamsSelectID,
			langsmith.RunQueryParamsSelectTotalTokens,
			langsmith.RunQueryParamsSelectTotalCost,
		}),
	})
	if err != nil {
		panic(err.Error())
	}
	for _, run := range runs.Runs {
		fmt.Println(run.ID, run.TotalTokens, run.TotalCost)
		// :remove-start:
		break
		// :remove-end:
	}
}
// :snippet-end:
