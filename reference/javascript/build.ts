import { execSync } from "child_process";
import { installDependencies } from "nypm";
import { type TypeDocOptions, Application } from "typedoc";
import fs from "fs";
import path from "path";

/**
 * A reference to a remote repository
 */
type Remote = {
  /**
   * The GitHub repository in the format "owner/repo".
   */
  repo: string;
  /**
   * The branch to use from the repository. Defaults to "main" if not specified.
   */
  branch?: string;
};

/**
 * A reference to a package in a remote repository that should be included in reference docs.
 */
type Package = Remote & {
  /**
   * The name of the package (as published to npm).
   */
  package: string;
  /**
   * The relative path to the package within the repository.
   */
  path: string;
  /**
   * Whether to run package installation for this package.
   * If true, dependencies will be installed from the package directory
   * instead of the remote's root directory
   */
  packageInstall?: boolean;
};

type PackageGroup = {
  group: string;
  items: Package[];
};

type Source = PackageGroup | Package;

const DIST_DIR = path.resolve(__dirname, "..", "dist", "javascript");

const SOURCES: Source[] = [
  {
    package: "langchain",
    path: "libs/langchain",
    repo: "langchain-ai/langchainjs",
    branch: "main",
  },
  {
    package: "@langchain/core",
    path: "libs/langchain-core",
    repo: "langchain-ai/langchainjs",
    branch: "main",
  },
  {
    package: "@langchain/textsplitters",
    path: "libs/langchain-textsplitters",
    repo: "langchain-ai/langchainjs",
    branch: "main",
  },
  {
    package: "@langchain/classic",
    path: "libs/langchain-classic",
    repo: "langchain-ai/langchainjs",
    branch: "main",
  },
  {
    group: "Integrations",
    items: [
      {
        package: "@langchain/community",
        path: "libs/langchain-community",
        repo: "langchain-ai/langchainjs",
        branch: "main",
      },
      {
        package: "@langchain/anthropic",
        path: "libs/providers/langchain-anthropic",
        repo: "langchain-ai/langchainjs",
        branch: "main",
      },
      {
        package: "@langchain/aws",
        path: "libs/providers/langchain-aws",
        repo: "langchain-ai/langchainjs",
        branch: "main",
      },
      {
        package: "@langchain/deepseek",
        path: "libs/providers/langchain-deepseek",
        repo: "langchain-ai/langchainjs",
        branch: "main",
      },
      {
        package: "@langchain/google-genai",
        path: "libs/providers/langchain-google-genai",
        repo: "langchain-ai/langchainjs",
        branch: "main",
      },
      {
        package: "@langchain/google-vertexai-web",
        path: "libs/providers/langchain-google-vertexai-web",
        repo: "langchain-ai/langchainjs",
        branch: "main",
      },
      {
        package: "@langchain/google-vertexai",
        path: "libs/providers/langchain-google-vertexai",
        repo: "langchain-ai/langchainjs",
        branch: "main",
      },
      {
        package: "@langchain/groq",
        path: "libs/providers/langchain-groq",
        repo: "langchain-ai/langchainjs",
        branch: "main",
      },
      {
        package: "@langchain/mistralai",
        path: "libs/providers/langchain-mistralai",
        repo: "langchain-ai/langchainjs",
        branch: "main",
      },
      {
        package: "@langchain/ollama",
        path: "libs/providers/langchain-ollama",
        repo: "langchain-ai/langchainjs",
        branch: "main",
      },
      {
        package: "@langchain/openai",
        path: "libs/providers/langchain-openai",
        repo: "langchain-ai/langchainjs",
        branch: "main",
      },
      {
        package: "@langchain/xai",
        path: "libs/providers/langchain-xai",
        repo: "langchain-ai/langchainjs",
        branch: "main",
      },
    ],
  },
  {
    group: "LangGraph",
    items: [
      {
        package: "@langchain/langgraph-checkpoint-mongodb",
        path: "libs/checkpoint-mongodb",
        repo: "langchain-ai/langgraphjs",
        branch: "main",
      },
      {
        package: "@langchain/langgraph-checkpoint-postgres",
        path: "libs/checkpoint-postgres",
        repo: "langchain-ai/langgraphjs",
        branch: "main",
      },
      {
        package: "@langchain/langgraph-checkpoint-redis",
        path: "libs/checkpoint-redis",
        repo: "langchain-ai/langgraphjs",
        branch: "main",
      },
      {
        package: "@langchain/langgraph-checkpoint-sqlite",
        path: "libs/checkpoint-sqlite",
        repo: "langchain-ai/langgraphjs",
        branch: "main",
      },
      {
        package: "@langchain/langgraph-checkpoint",
        path: "libs/checkpoint",
        repo: "langchain-ai/langgraphjs",
        branch: "main",
      },
      {
        package: "@langchain/langgraph-api",
        path: "libs/langgraph-api",
        repo: "langchain-ai/langgraphjs",
        branch: "main",
      },
      {
        package: "@langchain/langgraph-cli",
        path: "libs/langgraph-cli",
        repo: "langchain-ai/langgraphjs",
        branch: "main",
      },
      {
        package: "@langchain/langgraph-cua",
        path: "libs/langgraph-cua",
        repo: "langchain-ai/langgraphjs",
        branch: "main",
      },
      {
        package: "@langchain/langgraph-supervisor",
        path: "libs/langgraph-supervisor",
        repo: "langchain-ai/langgraphjs",
        branch: "main",
      },
      {
        package: "@langchain/langgraph-swarm",
        path: "libs/langgraph-swarm",
        repo: "langchain-ai/langgraphjs",
        branch: "main",
      },
      {
        package: "@langchain/langgraph-ui",
        path: "libs/langgraph-ui",
        repo: "langchain-ai/langgraphjs",
        branch: "main",
      },
      {
        package: "@langchain/langgraph",
        path: "libs/langgraph-core",
        repo: "langchain-ai/langgraphjs",
        branch: "main",
      },
      {
        package: "@langchain/langgraph-sdk",
        path: "libs/sdk",
        repo: "langchain-ai/langgraphjs",
        branch: "main",
      },
    ],
  },
  {
    group: "LangSmith",
    items: [
      {
        package: "langsmith",
        path: "js",
        repo: "langchain-ai/langsmith-sdk",
        branch: "main",
        packageInstall: true,
      },
    ],
  },
  {
    package: "deepagents",
    path: "libs/deepagents",
    repo: "langchain-ai/deepagentsjs",
    branch: "main",
  }
];

const ROOT_TYPEDOC_CONFIG: TypeDocOptions = {
  out: "public",
  sort: [
    "kind",
    "visibility",
    "instance-first",
    "required-first",
    "alphabetical",
  ],
  plugin: ["typedoc-plugin-expand-object-like-types", path.join(__dirname, "plugins/gtm")],
  gtmId: "GTM-MBBX68ST",
  logLevel: "Error",
  name: "langchain.js",
  hostedBaseUrl: "https://reference.langchain.com/javascript",
  useHostedBaseUrlForAbsoluteLinks: false,
  readme: "none",
  entryPointStrategy: "packages",
  includeVersion: true,
};

const PACKAGE_TYPEDOC_CONFIG: TypeDocOptions = {
  excludePrivate: true,
  excludeInternal: true,
  excludeExternals: true,
  excludeNotDocumented: false,
  includeVersion: true,
  categorizeByGroup: true,
  skipErrorChecking: true,
};

const iife = <T>(fn: () => T) => fn();

const exec = (args: string[]) =>
  execSync(args.join(" "), { encoding: "utf-8", stdio: "inherit" });

/**
 * Reads a JSON file, applies a transformation function to its contents, and writes the result back to the file.
 *
 * @param {string} relativePath - The path to the JSON file, relative to the current working directory.
 * @param {(json: any) => any} fn - A function that takes the parsed JSON object and returns the modified object.
 */
const updateJsonFile = (relativePath: string, fn: (json: any) => any) => {
  const contents = fs.readFileSync(relativePath).toString();
  const res = fn(JSON.parse(contents));
  fs.writeFileSync(relativePath, JSON.stringify(res, null, 2) + "\n");
};

/**
 * Constructs the target filesystem path for a given remote repository and branch.
 *
 * @param {Remote} remote - The remote repository object containing the repo name and optional branch.
 * @returns {string} The absolute path to the target directory for the specified remote and branch.
 */
const remotePath = (remote: Remote) =>
  path.join(__dirname, "remotes", remote.repo, remote.branch ?? "main");

/**
 * Constructs the absolute filesystem path for a given package.
 *
 * @param {Package} pkg - The package object containing the path and remote information.
 * @returns {string} The absolute path to the package directory.
 */
const packagePath = (pkg: Package) => path.join(remotePath(pkg), pkg.path);

/**
 * Recursively iterates over a list of sources, yielding each individual package.
 *
 * If a source is a group (i.e., has a "group" property), this function will recursively
 * iterate over its items. Otherwise, it yields the source as a package.
 *
 * @param {Source[]} sources - The array of sources to iterate over. Each source can be either a group or a package.
 * @yields {Package} Each package found in the sources, including those nested within groups.
 */
function* iteratePackages(sources: Source[]): Iterable<Package> {
  for (const source of sources) {
    if ("group" in source) {
      yield* iteratePackages(source.items);
    } else {
      yield source;
    }
  }
}

/**
 * Reduces all packages found in the given sources into a single accumulated value.
 *
 * This function flattens all packages (recursively, if sources contain groups) and applies
 * the provided reducer function to accumulate a result.
 *
 * @template T The type of the accumulated value.
 * @param {Source[]} sources - The array of sources to process. Each source can be a group or a package.
 * @param {(acc: T, pkg: Package) => T} fn - The reducer function, called with the accumulator and each package.
 * @param {T} initial - The initial value for the accumulator.
 * @returns {T} The final accumulated value after processing all packages.
 */
function reducePackages<T>(
  sources: Source[],
  fn: (acc: T, pkg: Package) => T,
  initial: T
): T {
  return Array.from(iteratePackages(sources)).reduce(fn, initial);
}

/**
 * Fetches the latest commit SHA for a given remote GitHub repository and branch.
 *
 * @param {Remote} remote - The remote repository object containing:
 *   - repo: The GitHub repository in the format "owner/repo".
 *   - branch (optional): The branch to fetch the latest commit SHA from. Defaults to "main" if not specified.
 * @returns {Promise<string>} The SHA of the latest commit on the specified branch.
 */
async function getLatestRemoteSha(remote: Remote): Promise<string> {
  const branch = remote.branch ?? "main";
  const apiUrl = `https://api.github.com/repos/${remote.repo}/commits/${branch}`;
  // These headers aren't explicitly required by GitHub, but we include them
  // if they are present to avoid rate limiting.
  const headers: Record<string, string> = process.env.GITHUB_TOKEN
    ? {
        Authorization: `Bearer ${process.env.GITHUB_TOKEN}`,
        "X-GitHub-Api-Version": "2022-11-28",
      }
    : {};
  const res = await fetch(apiUrl, { headers });
  const data = await res.json();
  return data.sha;
}

/**
 * Retrieves the locally cached commit SHA for the specified remote branch.
 *
 * Reads the SHA stored in a `.sha` file inside the `remotePath(remote)` directory.
 * If the cache file does not exist, returns an empty string.
 *
 * @param {Remote} remote - The remote repository reference.
 * @returns {Promise<string>} The cached SHA string, or an empty string if not present.
 */
async function getLocalRemoteSha(remote: Remote) {
  const shaFile = path.join(remotePath(remote), ".sha");
  if (fs.existsSync(shaFile)) {
    try {
      const res = fs.readFileSync(shaFile, "utf-8");
      return res.toString().trim();
    } catch {
      return "";
    }
  }
  return "";
}

/**
 * Ensures that the local copy of a remote GitHub repository branch is up to date.
 *
 * - Compares the latest remote commit SHA with a locally cached SHA (stored in `.sha`).
 * - If up to date, no action is taken. Otherwise, downloads and extracts the branch tarball.
 *
 * @param {Remote} remote - The remote repository reference.
 * @returns {Promise<void>} Resolves when the local copy is ensured to be up to date.
 */
async function ensureLatestRemote(remote: Remote) {
  const latestSha = await getLatestRemoteSha(remote);
  const localSha = await getLocalRemoteSha(remote);
  if (fs.existsSync(remotePath(remote)) && latestSha === localSha) return;
  pullRemote(remote, latestSha);
}

/**
 * Downloads a GitHub branch tarball and extracts it to the target directory.
 *
 * @param {Remote} remote - The remote repository reference.
 * @param {string} latestSha - The latest commit SHA for the target branch to cache locally.
 *
 * The tarball at `https://github.com/<repo>/archive/refs/heads/<branch>.tar.gz` is
 * streamed to `tar` with `--strip-components=1` so the contents are extracted directly
 * into the directory returned by `remotePath(remote)`.
 */
function pullRemote(remote: Remote, latestSha: string) {
  const branch = remote.branch ?? "main";
  const target = remotePath(remote);
  const url = `https://github.com/${remote.repo}/archive/refs/heads/${branch}.tar.gz`;
  console.info(`Fetching remote tarball ${remote.repo}/${branch}`);
  if (fs.existsSync(target)) {
    fs.rmSync(target, { recursive: true, force: true });
  }
  exec(["mkdir -p", target]);
  exec([`curl -L -s`, url, `| tar -xz --strip-components=1 -C`, target]);
  const shaFile = path.join(target, ".sha");
  fs.writeFileSync(shaFile, `${latestSha}\n`);
}

/**
 * Ensures that the TypeDoc configuration file (`typedoc.json`) exists and is properly configured
 * for the given package. This function reads the package's `package.json` to determine its entry points
 * (based on the "exports" field), and then writes or updates the `typedoc.json` file in the package's
 * directory to include these entry points and extend from the root TypeDoc config.
 *
 * - If `typedoc.json` does not exist, it will be created as an empty object before updating.
 * - The "entryPoints" field in the config will be set to the entry points found in the package's exports.
 * - The "extends" field will be set to reference the root TypeDoc config.
 *
 * @param {Package} pkg - The package for which to flush (write/update) the TypeDoc config.
 */
function ensurePackageTypedocConfig(pkg: Package) {
  const packageJsonPath = path.join(remotePath(pkg), pkg.path, "package.json");
  const typedocConfigPath = path.join(
    remotePath(pkg),
    pkg.path,
    "typedoc.json"
  );

  const packageEntrypoints = iife(() => {
    const packageJson = require(packageJsonPath);
    const exports: Record<string, any> =
      "exports" in packageJson && typeof packageJson.exports === "object"
        ? packageJson.exports
        : {};
    return Object.values(exports).reduce<string[]>((acc, value) => {
      if (
        typeof value === "object" &&
        "input" in value &&
        typeof value.input === "string"
      ) {
        acc.push(value.input);
      }
      return acc;
    }, []);
  });

  if (!fs.existsSync(typedocConfigPath)) {
    fs.writeFileSync(typedocConfigPath, "{}");
  }
  updateJsonFile(typedocConfigPath, () => ({
    ...PACKAGE_TYPEDOC_CONFIG,
    entryPoints: packageEntrypoints,
    includeVersion: true,
  }));
}

async function build() {
  const remotes = reducePackages<Remote[]>(
    SOURCES,
    (acc, pkg) => {
      const existing = acc.find(
        (r) => r.repo === pkg.repo && r.branch === pkg.branch
      );
      if (!existing) acc.push({ repo: pkg.repo, branch: pkg.branch });
      return acc;
    },
    []
  );
  const packages = Array.from(iteratePackages(SOURCES));

  await Promise.all(remotes.map((r) => ensureLatestRemote(r)));

  const installTargets = reducePackages<Array<Package | Remote>>(
    SOURCES,
    (acc, pkg) => {
      if (pkg.packageInstall) acc.push(pkg);
      else {
        const existingRemote = acc.find(
          (r) => r.repo === pkg.repo && r.branch === pkg.branch
        );
        if (!existingRemote) acc.push({ repo: pkg.repo, branch: pkg.branch });
      }
      return acc;
    },
    []
  );

  await Promise.all(
    installTargets.map(async (t) => {
      console.info(
        `Installing dependencies for ${t.repo}/${t.branch ?? "main"}`
      );
      if ("package" in t) {
        await installDependencies({ cwd: packagePath(t), silent: true });
      } else {
        await installDependencies({ cwd: remotePath(t), silent: true });
      }
    })
  );

  for (const p of packages) {
    ensurePackageTypedocConfig(p);
  }

  const entrypoints = packages.map((pkg) =>
    path.join(remotePath(pkg), pkg.path)
  );

  console.info(`Generating docs for ${entrypoints.length} entrypoints`);

  const app = await Application.bootstrapWithPlugins({
    ...ROOT_TYPEDOC_CONFIG,
    entryPoints: entrypoints,
  });

  const reflection = await app.convert();
  if (reflection) {
    console.info(`Writing docs to ${DIST_DIR}`);
    await app.generateDocs(reflection, DIST_DIR);
  }

  console.info("Done");
}

if (require.main === module) {
  build();
}
