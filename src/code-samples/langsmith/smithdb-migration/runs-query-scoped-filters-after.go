// :snippet-start: runs-query-scoped-filters-after-go
// :codegroup-tab: After
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

runs, err := client.Runs.QueryV2(ctx, langsmith.RunQueryV2Params{
	ProjectIDs:  langsmith.F([]string{project.ID}),
	Filter:      langsmith.F(`eq(name, "RetrieveDocs")`),
	TraceFilter: langsmith.F(`and(eq(feedback_key, "user_score"), eq(feedback_score, 1))`),
	TreeFilter:  langsmith.F(`eq(name, "ExpandQuery")`),
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
