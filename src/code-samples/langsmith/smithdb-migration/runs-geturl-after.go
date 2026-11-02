// :snippet-start: runs-geturl-after-go
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

	runID := "<run-id>"
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

	runs, err := client.Runs.QueryV2(ctx, langsmith.RunQueryV2Params{
		ProjectIDs:   langsmith.F([]string{projectID}),
		MinStartTime: langsmith.F(time.Now().UTC().AddDate(0, -1, 0)),
		PageSize:     langsmith.F(int64(1)),
	})
	if err != nil {
		panic(err.Error())
	}
	runID = runs.Items[0].ID
	// :remove-end:
	run, err := client.Runs.GetV2(ctx, runID, langsmith.RunGetV2Params{
		ProjectID: langsmith.F(projectID),
		Selects: langsmith.F([]langsmith.RunGetV2ParamsSelect{
			langsmith.RunGetV2ParamsSelectID,
			langsmith.RunGetV2ParamsSelectProjectID,
			langsmith.RunGetV2ParamsSelectTraceID,
			langsmith.RunGetV2ParamsSelectStartTime,
		}),
	})
	if err != nil {
		panic(err.Error())
	}

	response, err := client.Runs.GetURL(ctx, run.ID, langsmith.RunGetURLParams{
		ProjectID: langsmith.F(run.ProjectID),
		TraceID:   langsmith.F(run.TraceID),
		StartTime: langsmith.F(run.StartTime.Format(time.RFC3339)), // Optional, but speeds up retrieval
	})
	if err != nil {
		panic(err.Error())
	}
	fmt.Println(response.URL)
}
// :snippet-end:
