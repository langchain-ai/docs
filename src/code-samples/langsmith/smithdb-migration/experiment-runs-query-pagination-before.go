// :snippet-start: experiment-runs-query-pagination-before-go
// :codegroup-tab: Before
package main

import (
	"context"

	"github.com/langchain-ai/langsmith-go"
)

// :remove-start:
var datasetID = "00000000-0000-0000-0000-000000000000"
var experimentID = "00000000-0000-0000-0000-000000000001"

func main() {
	if false {
// :remove-end:
ctx := context.Background()
client := langsmith.NewClient()

examplesWithRuns, err := client.Datasets.Runs.Query(ctx, datasetID, langsmith.DatasetRunQueryParams{
	SessionIDs: langsmith.F([]string{experimentID}),
	Limit:      langsmith.F(int64(20)),
	Offset:     langsmith.F(int64(20)),
})
// :remove-start:
if err != nil {
	panic(err.Error())
}
_ = examplesWithRuns
	}
}
// :remove-end:
// :snippet-end:
