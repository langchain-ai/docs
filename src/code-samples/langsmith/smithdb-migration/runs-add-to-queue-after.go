// :snippet-start: runs-add-to-queue-after-go
// :codegroup-tab: After
package main

import (
	"context"
	"time"

	"github.com/langchain-ai/langsmith-go"
)

// :remove-start:
func main() {
// :remove-end:
ctx := context.Background()
client := langsmith.NewClient()

queueID := "<queue-id>"
projectID := "<project-id>"
// :remove-start:
sessions, err := client.Sessions.List(ctx, langsmith.SessionListParams{
	Name:  langsmith.F("default"),
	Limit: langsmith.F(int64(1)),
})
if err != nil {
	panic(err.Error())
}
projectID = sessions.Items[0].ID
queue, err := client.AnnotationQueues.AnnotationQueues(ctx, langsmith.AnnotationQueueAnnotationQueuesParams{
	Name: langsmith.F("docs-smithdb-migration-" + time.Now().Format("20060102150405.000000000")),
})
if err != nil {
	panic(err.Error())
}
queueID = queue.ID
// :remove-end:
found, err := client.Runs.QueryV2(ctx, langsmith.RunQueryV2Params{
	ProjectIDs:   langsmith.F([]string{projectID}),
	MinStartTime: langsmith.F(time.Now().UTC().AddDate(0, 0, -30)),
	Selects: langsmith.F([]langsmith.RunSelectField{
		langsmith.RunSelectFieldID,
		langsmith.RunSelectFieldProjectID,
		langsmith.RunSelectFieldStartTime,
	}),
	PageSize: langsmith.F(int64(5)),
})
// :remove-start:
if err != nil {
	panic(err.Error())
}
// :remove-end:
items := make([]langsmith.AnnotationQueueItemNewParamsItem, len(found.Items))
for i, run := range found.Items {
	items[i] = langsmith.AnnotationQueueItemNewParamsItem{
		ItemType:  langsmith.F(langsmith.AnnotationQueueItemNewParamsItemsItemTypeRun),
		RunID:     langsmith.F(run.ID),
		ProjectID: langsmith.F(run.ProjectID),
		StartTime: langsmith.F(run.StartTime),
	}
}
_, err = client.AnnotationQueues.Items.New(ctx, queueID, langsmith.AnnotationQueueItemNewParams{
	Items: langsmith.F(items),
})
// :remove-start:
if err != nil {
	panic(err.Error())
}
}

// :remove-end:
// :snippet-end:
