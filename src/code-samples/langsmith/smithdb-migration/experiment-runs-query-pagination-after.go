// :snippet-start: experiment-runs-query-pagination-after-go
// :codegroup-tab: After
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

iter := client.Datasets.ExperimentRuns.QueryAutoPaging(ctx, datasetID, langsmith.DatasetExperimentRunQueryParams{
	ExperimentIDs: langsmith.F([]string{experimentID}),
	PageSize:      langsmith.F(int64(20)),
})
for iter.Next() {
	run := iter.Current()
	// :remove-start:
	_ = run
	// :remove-end:
}
// :remove-start:
if err := iter.Err(); err != nil {
	panic(err.Error())
}
	}
}
// :remove-end:
// :snippet-end:
