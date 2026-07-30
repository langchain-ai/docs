// :snippet-start: runs-query-fetch-by-id-before-go
// :codegroup-tab: Before
package main

import (
	"context"

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
found, err := client.Runs.Query(ctx, langsmith.RunQueryParams{
	Session: langsmith.F([]string{project.ID}),
	Limit:   langsmith.F(int64(2)),
})
if err != nil {
	panic(err.Error())
}
runID1 = found.Runs[0].ID
runID2 = found.Runs[1].ID
// :remove-end:
runs, err := client.Runs.Query(ctx, langsmith.RunQueryParams{
	Session: langsmith.F([]string{project.ID}),
	ID:      langsmith.F([]string{runID1, runID2}),
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
