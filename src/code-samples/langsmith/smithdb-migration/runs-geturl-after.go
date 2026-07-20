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

	sessions, err := client.Sessions.List(ctx, langsmith.SessionListParams{
		Name:  langsmith.F("default"),
		Limit: langsmith.F(int64(1)),
	})
	if err != nil {
		panic(err.Error())
	}
	project := sessions.Items[0]

	runs, err := client.Runs.QueryV2(ctx, langsmith.RunQueryV2Params{
		ProjectIDs: langsmith.F([]string{project.ID}),
		Selects: langsmith.F([]langsmith.RunSelectField{
			langsmith.RunSelectFieldID,
			langsmith.RunSelectFieldTraceID,
			langsmith.RunSelectFieldStartTime,
		}),
		PageSize: langsmith.F(int64(1)),
	})
	if err != nil {
		panic(err.Error())
	}
	run := runs.Items[0]

	response, err := client.Runs.GetURL(ctx, run.ID, langsmith.RunGetURLParams{
		ProjectID: langsmith.F(project.ID),
		TraceID:   langsmith.F(run.TraceID),
		StartTime: langsmith.F(run.StartTime.Format(time.RFC3339)),
	})
	if err != nil {
		panic(err.Error())
	}
	fmt.Println(response.URL)
}
// :snippet-end:
