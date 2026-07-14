
// :snippet-start: threads-stats-first-start-time-before-go
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
	threadFilter := fmt.Sprintf(`eq(thread_id, "%s")`, threadID)

	statsUnion, err := client.Runs.Stats(ctx, langsmith.RunStatsParams{
		RunStatsQueryParams: langsmith.RunStatsQueryParams{
			Session: langsmith.F([]string{projectID}),
			Filter:  langsmith.F(threadFilter),
			IsRoot:  langsmith.F(true),
		},
	})
	if err != nil {
		panic(err.Error())
	}
	runCount := int64(0)
	if stats, ok := (*statsUnion).(langsmith.RunStatsResponseRunStats); ok {
		runCount = stats.RunCount
	}

	// RunStatsQueryParams has no "first_start_time" field — a second call,
	// sorted ascending, is needed to find the thread's earliest run.
	runs, err := client.Runs.Query(ctx, langsmith.RunQueryParams{
		Session: langsmith.F([]string{projectID}),
		Filter:  langsmith.F(threadFilter),
		IsRoot:  langsmith.F(true),
		Order:   langsmith.F(langsmith.RunQueryParamsOrderAsc),
		Limit:   langsmith.F(int64(1)),
	})
	if err != nil {
		panic(err.Error())
	}
	var firstStartTime time.Time
	if len(runs.Runs) > 0 {
		firstStartTime = runs.Runs[0].StartTime
	}
	fmt.Println(runCount, firstStartTime)
}
// :snippet-end:
