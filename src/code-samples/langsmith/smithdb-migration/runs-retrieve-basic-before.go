// :snippet-start: runs-retrieve-basic-before-go
// :codegroup-tab: Before
package main

import (
	"context"
	"fmt"

	"github.com/langchain-ai/langsmith-go"
)

// :remove-start:
func main() {
// :remove-end:
ctx := context.Background()
client := langsmith.NewClient()

runID := "<run-id>"
// :remove-start:
sessions, err := client.Sessions.List(ctx, langsmith.SessionListParams{
	Name:  langsmith.F("default"),
	Limit: langsmith.F(int64(1)),
})
if err != nil {
	panic(err.Error())
}
found, err := client.Runs.Query(ctx, langsmith.RunQueryParams{
	Session: langsmith.F([]string{sessions.Items[0].ID}),
	Limit:   langsmith.F(int64(1)),
})
if err != nil {
	panic(err.Error())
}
runID = found.Runs[0].ID
// :remove-end:
run, err := client.Runs.Get(ctx, runID, langsmith.RunGetParams{})
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
