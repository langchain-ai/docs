// :snippet-start: runs-retrieve-not-found-after-go
// :codegroup-tab: After
package main

import (
	"context"
	"errors"
	"fmt"
	// :remove-start:
	"crypto/rand"
	// :remove-end:
	"time"

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

b := make([]byte, 16)
_, _ = rand.Read(b)
b[6] = (b[6] & 0x0f) | 0x40
b[8] = (b[8] & 0x3f) | 0x80
runID = fmt.Sprintf("%x-%x-%x-%x-%x", b[0:4], b[4:6], b[6:8], b[8:10], b[10:16])
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
