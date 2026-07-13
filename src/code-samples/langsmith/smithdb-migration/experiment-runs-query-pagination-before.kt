///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.13

// :snippet-start: experiment-runs-query-pagination-before-kt
// :codegroup-tab: Before
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.datasets.runs.RunQueryParams
// :remove-start:
import com.langchain.smith.models.datasets.DatasetCreateParams
import com.langchain.smith.models.datasets.DatasetListParams
import com.langchain.smith.models.examples.ExampleCreateParams
import com.langchain.smith.evaluation.EvaluateParams
import com.langchain.smith.evaluation.EvaluationResult
import com.langchain.smith.evaluation.evaluate
import com.langchain.smith.evaluation.runEvaluator
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
if (existingDatasets.isEmpty()) {
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
}

val correctness = runEvaluator { outputs: Map<String, Any?>, referenceOutputs: Map<String, Any?> ->
    EvaluationResult(
        key = "correctness",
        score = if (outputs["answer"] == referenceOutputs["answer"]) 1 else 0,
    )
}

val evalResults = evaluate(
    client,
    { inputs ->
        val (a, b) = (inputs["question"] as String).split(" + ").map { it.toInt() }
        mapOf("answer" to (a + b).toString())
    },
    EvaluateParams.builder()
        .data(fixtureDatasetName)
        .addEvaluator(correctness)
        .experimentPrefix("docs-experiment-runs-query-pagination")
        .build(),
)
val datasetId = evalResults.datasetId
val experimentId = evalResults.experimentId!!
// :remove-end:
val examplesWithRuns = client.datasets().runs().query(
    datasetId,
    RunQueryParams.builder()
        .addSessionId(experimentId)
        .limit(1L)
        .offset(1L)
        .build()
)
// :remove-start:
}
// :remove-end:
// :snippet-end:
