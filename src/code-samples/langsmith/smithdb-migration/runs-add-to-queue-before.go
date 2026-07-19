// :snippet-start: runs-add-to-queue-before-go
// :codegroup-tab: Before
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
found, err := client.Runs.Query(ctx, langsmith.RunQueryParams{
	Session: langsmith.F([]string{projectID}),
	Limit:   langsmith.F(int64(5)),
})
// :remove-start:
if err != nil {
	panic(err.Error())
}
// :remove-end:
runIDs := make([]string, len(found.Runs))
for i, run := range found.Runs {
	runIDs[i] = run.ID
}
_, err = client.AnnotationQueues.Runs.New(ctx, queueID, langsmith.AnnotationQueueRunNewParams{
	Body: langsmith.AnnotationQueueRunNewParamsBodyRunsUuidArray(runIDs),
})
// :remove-start:
if err != nil {
	panic(err.Error())
}
}

// :remove-end:
// :snippet-end:
