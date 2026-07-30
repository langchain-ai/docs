// :snippet-start: runs-retrieve-not-found-after-go
// :codegroup-tab: After
package main

import (
	"context"
	"errors"
	"fmt"
	"time"

	"github.com/google/uuid"
	"github.com/langchain-ai/langsmith-go"
)

// :remove-start:
func main() {
// :remove-end:
ctx := context.Background()
client := langsmith.NewClient()

runID := "<run-id>"
startTime := time.Date(2026, 6, 1, 12, 0, 0, 0, time.UTC)
projectID := "<project-id>"
// :remove-start:
sessions, sessErr := client.Sessions.List(ctx, langsmith.SessionListParams{
	Name:  langsmith.F("default"),
	Limit: langsmith.F(int64(1)),
})
if sessErr != nil {
	panic(sessErr.Error())
}
projectID = sessions.Items[0].ID

runID = uuid.New().String()
// :remove-end:
_, err := client.Runs.GetV2(ctx, runID, langsmith.RunGetV2Params{
	ProjectID: langsmith.F(projectID),
	StartTime: langsmith.F(startTime),
})
if err != nil {
	var apiErr *langsmith.Error
	if errors.As(err, &apiErr) && apiErr.StatusCode == 404 {
		fmt.Printf("Run %s not found\n", runID)
	} else {
		panic(err)
	}
}
// :remove-start:
}

// :remove-end:
// :snippet-end:
