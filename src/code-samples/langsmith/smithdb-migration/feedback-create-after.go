// :snippet-start: feedback-create-after-go
// :codegroup-tab: After
package main

import (
	"context"

	"github.com/langchain-ai/langsmith-go"
	"github.com/langchain-ai/langsmith-go/shared"
)

// :remove-start:
func main() {
// :remove-end:
ctx := context.Background()
client := langsmith.NewClient()

runID := "<run-id>"
sessionID := "<session-id>"
var err error
// :remove-start:
sessions, err := client.Sessions.List(ctx, langsmith.SessionListParams{
	Name:  langsmith.F("default"),
	Limit: langsmith.F(int64(1)),
})
if err != nil {
	panic(err.Error())
}
sessionID = sessions.Items[0].ID
found, err := client.Runs.Query(ctx, langsmith.RunQueryParams{
	Session: langsmith.F([]string{sessionID}),
	Limit:   langsmith.F(int64(1)),
})
if err != nil {
	panic(err.Error())
}
runID = found.Runs[0].ID
// :remove-end:
_, err = client.Feedback.New(ctx, langsmith.FeedbackNewParams{
	FeedbackCreateSchema: langsmith.FeedbackCreateSchemaParam{
		RunID:     langsmith.F(runID),
		Key:       langsmith.F("user_feedback"),
		Score:     langsmith.F[langsmith.FeedbackCreateSchemaScoreUnionParam](shared.UnionFloat(1.0)),
		SessionID: langsmith.F(sessionID),
	},
})
// :remove-start:
if err != nil {
	panic(err.Error())
}
}

// :remove-end:
// :snippet-end:
