// :snippet-start: experiment-runs-query-lookup-experiment-id-go
package main

import (
	"context"

	"github.com/langchain-ai/langsmith-go"
)

// :remove-start:
func main() {
	if false {
// :remove-end:
ctx := context.Background()
client := langsmith.NewClient()

sessions, err := client.Sessions.List(ctx, langsmith.SessionListParams{
	Name: langsmith.F("my-experiment"),
})
// :remove-start:
if err != nil {
	panic(err.Error())
}
// :remove-end:
experimentID := sessions.Items[0].ID
// :remove-start:
_ = experimentID
	}
}
// :remove-end:
// :snippet-end:
