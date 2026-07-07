// :snippet-start: experiment-runs-query-basic-after-go
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
	Selects: langsmith.F([]langsmith.DatasetExperimentRunQueryParamsSelect{
		langsmith.DatasetExperimentRunQueryParamsSelectID,
		langsmith.DatasetExperimentRunQueryParamsSelectName,
		langsmith.DatasetExperimentRunQueryParamsSelectStatus,
		langsmith.DatasetExperimentRunQueryParamsSelectInputsPreview,
		langsmith.DatasetExperimentRunQueryParamsSelectOutputsPreview,
	}),
})
// :remove-start:
if err != nil {
	panic(err.Error())
}
_ = page.Items
	}
}
// :remove-end:
// :snippet-end:
