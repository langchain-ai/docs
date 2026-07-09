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

page, err := client.Datasets.ExperimentRuns.Query(ctx, datasetID, langsmith.DatasetExperimentRunQueryParams{
	ExperimentIDs: langsmith.F([]string{experimentID}),
	PageSize:      langsmith.F(int64(20)),
})
// :remove-start:
if err != nil {
	panic(err.Error())
}
// :remove-end:
if page.NextCursor != "" {
	nextPage, err := client.Datasets.ExperimentRuns.Query(ctx, datasetID, langsmith.DatasetExperimentRunQueryParams{
		ExperimentIDs: langsmith.F([]string{experimentID}),
		PageSize:      langsmith.F(int64(20)),
		Cursor:        langsmith.F(page.NextCursor),
	})
	// :remove-start:
	if err != nil {
		panic(err.Error())
	}
	_ = nextPage
	// :remove-end:
}
// :remove-start:
	}
}
// :remove-end:
// :snippet-end:
