
// :snippet-start: threads-query-filter-status-before-go
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

	runs, err := client.Runs.Query(ctx, langsmith.RunQueryParams{
		Session: langsmith.F([]string{projectID}),
		IsRoot:  langsmith.F(true),
		Filter:  langsmith.F(`eq(status, "error")`),
	})
	if err != nil {
		panic(err.Error())
	}

	threads := map[string]string{}
	for _, run := range runs.Runs {
		metadata, ok := run.Extra["metadata"].(map[string]interface{})
		if !ok {
			continue
		}
		threadID, ok := metadata["thread_id"].(string)
		if ok {
			threads[threadID] = run.Error
		}
	}
	for threadID, lastError := range threads {
		fmt.Println(threadID, lastError)
	}
}
// :snippet-end:
