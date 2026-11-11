// :snippet-start: feedback-create-after-go
// :codegroup-tab: After
package main

import (
	"context"
	// :remove-start:
	"time"
	// :remove-end:

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
found, err := client.Runs.QueryV2(ctx, langsmith.RunQueryV2Params{
	ProjectIDs:   langsmith.F([]string{sessionID}),
	MinStartTime: langsmith.F(time.Now().UTC().AddDate(0, 0, -30)),
	PageSize:     langsmith.F(int64(1)),
})
if err != nil {
	panic(err.Error())
}
runID = found.Items[0].ID
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
