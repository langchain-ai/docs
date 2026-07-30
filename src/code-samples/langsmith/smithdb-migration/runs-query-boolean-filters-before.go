// :snippet-start: runs-query-boolean-filters-before-go
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

filterStr := `and(gt(start_time, "2023-07-15T12:34:56Z"), or(neq(status, "error"), and(eq(feedback_key, "Correctness"), eq(feedback_score, 0.0))))`
runs, err := client.Runs.Query(ctx, langsmith.RunQueryParams{
	Session: langsmith.F([]string{project.ID}),
	Filter:  langsmith.F(filterStr),
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
