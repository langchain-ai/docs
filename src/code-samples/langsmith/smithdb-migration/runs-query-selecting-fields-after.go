// :snippet-start: runs-query-selecting-fields-after-go
// :codegroup-tab: After
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

// must explicitly list every field needed; default returns only id
runs, err := client.Runs.QueryV2(ctx, langsmith.RunQueryV2Params{
	ProjectIDs: langsmith.F([]string{project.ID}),
	Selects: langsmith.F([]langsmith.RunSelectField{
		langsmith.RunSelectFieldID,
		langsmith.RunSelectFieldName,
		langsmith.RunSelectFieldRunType,
		langsmith.RunSelectFieldStatus,
		langsmith.RunSelectFieldStartTime,
		langsmith.RunSelectFieldInputs,
		langsmith.RunSelectFieldError,
	}),
})
// :remove-start:
if err != nil {
	panic(err.Error())
}
// :remove-end:
for _, run := range runs.Items {
	fmt.Println(run.ID, run.Name, run.RunType, run.Status, run.StartTime, run.Inputs, run.Error)
	// :remove-start:
	break
	// :remove-end:
}
// :remove-start:
}

// :remove-end:
// :snippet-end:
