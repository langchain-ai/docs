// :snippet-start: runs-query-selecting-fields-before-go
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

// returns a default set of fields; no explicit selection needed
runs, err := client.Runs.Query(ctx, langsmith.RunQueryParams{
	Session: langsmith.F([]string{project.ID}),
})
// :remove-start:
if err != nil {
	panic(err.Error())
}
// :remove-end:
for _, run := range runs.Runs {
	fmt.Println(run.ID, run.Name, run.RunType, run.Status, run.StartTime, run.Inputs, run.Error)
	// :remove-start:
	break
	// :remove-end:
}
// :remove-start:
}

// :remove-end:
// :snippet-end:
