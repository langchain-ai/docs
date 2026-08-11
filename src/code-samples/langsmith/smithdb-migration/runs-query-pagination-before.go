// :snippet-start: runs-query-pagination-before-go
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

runs := []langsmith.RunSchema{}
iter := client.Runs.QueryAutoPaging(ctx, langsmith.RunQueryParams{
	Session: langsmith.F([]string{project.ID}),
})
for iter.Next() {
	runs = append(runs, iter.Current())
	if len(runs) >= 150 {
		break
	}
}
// :remove-start:
if iter.Err() != nil {
	panic(iter.Err().Error())
}
// :remove-end:
// :remove-start:
}

// :remove-end:
// :snippet-end:
