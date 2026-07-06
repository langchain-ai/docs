///usr/bin/env jbang "$0" "$@" ; exit $?
//JAVA 21
//KOTLIN 2.2.0
//DEPS com.langchain.smith:langsmith-java:0.1.0-beta.11

// :snippet-start: experiment-runs-query-basic-after-kt
// :codegroup-tab: After
import com.langchain.smith.client.LangsmithClient
import com.langchain.smith.client.okhttp.LangsmithOkHttpClient
import com.langchain.smith.models.datasets.experimentruns.ExperimentRunCreateParams

// :remove-start:
fun main() {
    if (false) {
// :remove-end:
// :remove-start:
val datasetId = "00000000-0000-0000-0000-000000000000"
val experimentId = "00000000-0000-0000-0000-000000000001"
// :remove-end:
val client: LangsmithClient = LangsmithOkHttpClient.fromEnv()
val page = client.datasets().experimentRuns().create(
    datasetId,
    ExperimentRunCreateParams.builder()
        .addExperimentId(experimentId)
        .pageSize(20L)
        .addSelect(ExperimentRunCreateParams.Select.ID)
        .addSelect(ExperimentRunCreateParams.Select.NAME)
        .addSelect(ExperimentRunCreateParams.Select.STATUS)
        .addSelect(ExperimentRunCreateParams.Select.INPUTS_PREVIEW)
        .addSelect(ExperimentRunCreateParams.Select.OUTPUTS_PREVIEW)
        .build()
)
val examplesWithRuns = page.items()
// :remove-start:
    }
}
// :remove-end:
// :snippet-end:
