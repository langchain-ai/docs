// :snippet-start: runs-query-filter-time-range-before-go
// :codegroup-tab: Before
package main

import (
	"context"
	"time"

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

runs, err := client.Runs.Query(ctx, langsmith.RunQueryParams{
	Session:   langsmith.F([]string{project.ID}),
	StartTime: langsmith.F(time.Now().Add(-24 * time.Hour)),
	RunType:   langsmith.F(langsmith.RunTypeEnumLlm),
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
