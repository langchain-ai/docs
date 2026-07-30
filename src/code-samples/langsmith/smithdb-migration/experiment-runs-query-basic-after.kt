///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.18

// :snippet-start: experiment-runs-query-basic-after-kt
// :codegroup-tab: After
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.datasets.experimentruns.ExperimentRunQueryParams
import com.langchain.smith.models.runs.RunSelectField
// :remove-start:
import com.langchain.smith.models.datasets.DatasetCreateParams
import com.langchain.smith.models.datasets.DatasetListParams
import com.langchain.smith.models.examples.ExampleCreateParams
import com.langchain.smith.models.examples.ExampleListParams
import com.langchain.smith.models.sessions.SessionCreateParams
import com.langchain.smith.models.sessions.SessionListParams
import com.langchain.smith.models.runs.RunIngest
import com.langchain.smith.models.feedback.FeedbackCreateSchema
import java.time.OffsetDateTime
import java.util.UUID
// :remove-end:

// :remove-start:
fun main() {
// :remove-end:
val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()
// :remove-start:
val fixtureDatasetName = "docs-experiment-runs-query-fixture"
val existingDatasets = client.datasets().list(
    DatasetListParams.builder().name(fixtureDatasetName).build()
).items()
val fixtureDatasetId = if (existingDatasets.isNotEmpty()) {
    existingDatasets.first().id()
} else {
    val created = client.datasets().create(
        DatasetCreateParams.builder().name(fixtureDatasetName).build()
    )
    listOf("2 + 2" to "4", "3 + 3" to "6", "4 + 4" to "9").forEach { (question, answer) ->
        client.examples().create(
            ExampleCreateParams.builder()
                .datasetId(created.id())
                .inputs(
                    ExampleCreateParams.Inputs.builder()
                        .putAdditionalProperty("question", com.langchain.smith.core.JsonValue.from(question))
                        .build()
                )
                .outputs(
                    ExampleCreateParams.Outputs.builder()
                        .putAdditionalProperty("answer", com.langchain.smith.core.JsonValue.from(answer))
                        .build()
                )
                .build()
        )
    }
    created.id()
}
val datasetId = fixtureDatasetId

// The experiment is shared across every experiment-runs-query sample (this
// file and its siblings): created once, ever, and reused afterward so the
// suite doesn't spend a real evaluation run per file.
val experimentName = "docs-experiment-runs-query-fixture-experiment"
val existingSessions = client.sessions().list(
    SessionListParams.builder().name(experimentName).build()
).items()
val experimentId = if (existingSessions.isNotEmpty()) {
    existingSessions.first().id()
} else {
    val session = client.sessions().create(
        SessionCreateParams.builder()
            .name(experimentName)
            .referenceDatasetId(fixtureDatasetId)
            .build()
    )
    val fixtureAnswers = listOf("4" to "4", "6" to "6", "9" to "8")
    val examples = client.examples().list(
        ExampleListParams.builder().dataset(fixtureDatasetId).build()
    ).items()
    examples.zip(fixtureAnswers).forEach { (example, referenceAndTarget) ->
        val (referenceAnswer, targetAnswer) = referenceAndTarget
        val runId = UUID.randomUUID().toString()
        val now = OffsetDateTime.now().toString()
        client.runs().create(
            RunIngest.builder()
                .id(runId)
                .name("target")
                .runType(RunIngest.RunType.CHAIN)
                .sessionId(session.id())
                .referenceExampleId(example.id())
                .inputs(
                    RunIngest.Inputs.builder()
                        .putAllAdditionalProperties(example.inputs()._additionalProperties())
                        .build()
                )
                .outputs(
                    RunIngest.Outputs.builder()
                        .putAdditionalProperty("answer", com.langchain.smith.core.JsonValue.from(targetAnswer))
                        .build()
                )
                .startTime(now)
                .endTime(now)
                .build()
        )
        val score = if (targetAnswer == referenceAnswer) 1.0 else 0.0
        client.feedback().create(
            FeedbackCreateSchema.builder()
                .key("correctness")
                .runId(runId)
                .score(score)
                .build()
        )
    }
    // Sorting queries derive their time window from the experiment's start
    // time, truncated to whole seconds server-side. A short buffer avoids a
    // same-second min/max window on whichever run performs this creation.
    Thread.sleep(1000)
    session.id()
}
// :remove-end:
val page = client.datasets().experimentRuns().query(
    datasetId,
    ExperimentRunQueryParams.builder()
        .addExperimentId(experimentId)
        .pageSize(20L)
        .addSelect(RunSelectField.ID)
        .addSelect(RunSelectField.NAME)
        .addSelect(RunSelectField.STATUS)
        .addSelect(RunSelectField.INPUTS_PREVIEW)
        .addSelect(RunSelectField.OUTPUTS_PREVIEW)
        .build()
)
val examplesWithRuns = page.items()
// :remove-start:
}
// :remove-end:
// :snippet-end:
