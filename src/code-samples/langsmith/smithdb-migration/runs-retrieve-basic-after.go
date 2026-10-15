// :snippet-start: runs-retrieve-basic-after-go
// :codegroup-tab: After
package main

import (
	"context"
	"fmt"
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
sessions, err := client.Sessions.List(ctx, langsmith.SessionListParams{
	Name:  langsmith.F("default"),
	Limit: langsmith.F(int64(1)),
})
if err != nil {
	panic(err.Error())
}
projectID = sessions.Items[0].ID
maxStart := time.Now().UTC()
minStart := maxStart.AddDate(0, -1, 0)
found, err := client.Runs.QueryV2(ctx, langsmith.RunQueryV2Params{
	ProjectIDs:   langsmith.F([]string{projectID}),
	MinStartTime: langsmith.F(minStart),
	MaxStartTime: langsmith.F(maxStart),
	Selects: langsmith.F([]langsmith.RunSelectField{
		langsmith.RunSelectFieldID,
		langsmith.RunSelectFieldStartTime,
	}),
	PageSize: langsmith.F(int64(1)),
})
if err != nil {
	panic(err.Error())
}
runID = found.Items[0].ID
startTime = found.Items[0].StartTime
// :remove-end:
run, err := client.Runs.GetV2(ctx, runID, langsmith.RunGetV2Params{
	ProjectID: langsmith.F(projectID),
	StartTime: langsmith.F(startTime),
	Selects: langsmith.F([]langsmith.RunGetV2ParamsSelect{
		langsmith.RunGetV2ParamsSelectName,
		langsmith.RunGetV2ParamsSelectStatus,
		langsmith.RunGetV2ParamsSelectTotalTokens,
	}),
})
// :remove-start:
if err != nil {
	panic(err.Error())
}
// :remove-end:
fmt.Println(run.Name, run.Status, run.TotalTokens)
// :remove-start:
}

// :remove-end:
// :snippet-end:
