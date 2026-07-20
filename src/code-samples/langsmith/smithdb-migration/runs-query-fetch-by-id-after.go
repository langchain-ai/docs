// :snippet-start: runs-query-fetch-by-id-after-go
// :codegroup-tab: After
package main

import (
	"context"
	// :remove-start:
	"time"
	// :remove-end:

	"github.com/langchain-ai/langsmith-go"
)

// :remove-start:
func main() {
// :remove-end:
ctx := context.Background()
client := langsmith.NewClient()

sessions, err := client.Sessions.List(ctx, langsmith.SessionListParams{
	Name:  langsmith.F("default"),
	Limit: langsmith.F(int64(1)),
})
// :remove-start:
if err != nil {
	panic(err.Error())
}
// :remove-end:
project := sessions.Items[0]

runID1 := "<run-id-1>"
runID2 := "<run-id-2>"
// :remove-start:
maxStart := time.Now().UTC()
minStart := maxStart.AddDate(0, -1, 0)
found, err := client.Runs.QueryV2(ctx, langsmith.RunQueryV2Params{
	ProjectIDs:   langsmith.F([]string{project.ID}),
	MinStartTime: langsmith.F(minStart),
	MaxStartTime: langsmith.F(maxStart),
	PageSize:     langsmith.F(int64(2)),
})
if err != nil {
	panic(err.Error())
}
runID1 = found.Items[0].ID
runID2 = found.Items[1].ID
// :remove-end:
runs, err := client.Runs.QueryV2(ctx, langsmith.RunQueryV2Params{
	ProjectIDs: langsmith.F([]string{project.ID}),
	IDs:        langsmith.F([]string{runID1, runID2}),
})
// :remove-start:
if err != nil {
	panic(err.Error())
}
_ = runs
// :remove-end:
// :remove-start:
}

// :remove-end:
// :snippet-end:
