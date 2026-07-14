
// :snippet-start: threads-stats-basic-before-go
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

	statsUnion, err := client.Runs.Stats(ctx, langsmith.RunStatsParams{
		RunStatsQueryParams: langsmith.RunStatsQueryParams{
			Session: langsmith.F([]string{projectID}),
			Filter:  langsmith.F(fmt.Sprintf(`eq(thread_id, "%s")`, threadID)),
			IsRoot:  langsmith.F(true),
		},
	})
	if err != nil {
		panic(err.Error())
	}
	// RunStatsResponseUnion is ambiguous between a flat and a grouped shape;
	// a non-grouped response can decode as either depending on the SDK version.
	switch stats := (*statsUnion).(type) {
	case langsmith.RunStatsResponseRunStats:
		fmt.Println(stats.RunCount, stats.TotalTokens, stats.TotalCost)
	case langsmith.RunStatsResponseMap:
		fmt.Println("ambiguous response, entries:", len(stats))
	}
}
// :snippet-end:
