#!/usr/bin/env node

const fs = require("node:fs");
const path = require("node:path");

const rootDir = path.resolve(__dirname, "..", "..");
const wasmModulePath = path.join(rootDir, "build", "wasm", "cjbench_wasm.js");

function main() {
  const config = parseArgs(process.argv.slice(2));
  const wasm = require(wasmModulePath);
  const inputBytes = fs.readFileSync(config.input);

  for (let index = 0; index < config.warmup; index += 1) {
    execute(wasm, config, inputBytes);
  }

  const samplesNs = [];
  let lastOutcome = null;
  for (let index = 0; index < config.iterations; index += 1) {
    const started = process.hrtime.bigint();
    const outcome = execute(wasm, config, inputBytes);
    samplesNs.push(Number(process.hrtime.bigint() - started));
    lastOutcome = outcome;
  }

  let artifactOutcome = null;
  if (config.operation === "roundtrip") {
    artifactOutcome = execute(wasm, config, inputBytes);
    if (artifactOutcome.output === null) {
      throw new Error("roundtrip did not produce output bytes while writing artifact");
    }
    fs.mkdirSync(path.dirname(config.output), { recursive: true });
    fs.writeFileSync(config.output, artifactOutcome.output);
  }

  const outcome = artifactOutcome ?? lastOutcome;
  if (outcome === null) {
    throw new Error("no benchmark outcome");
  }

  const result = {
    target: "wasm",
    operation: config.operation,
    input: config.input,
    input_bytes: inputBytes.length,
    iterations: config.iterations,
    warmup: config.warmup,
    pretty_output: config.prettyOutput,
    samples_ns: samplesNs,
    output_bytes: outcome.output === null ? null : outcome.output.length,
    probe: outcome.probe,
    summary: outcome.summary,
    portability_note:
      "Benchmarks cjlib-wasm through a real wasm32-unknown-unknown module loaded by Node.js.",
  };

  fs.mkdirSync(path.dirname(config.resultJson), { recursive: true });
  fs.writeFileSync(config.resultJson, JSON.stringify(result, null, 2));
}

function execute(wasm, config, inputBytes) {
  switch (config.operation) {
    case "probe":
      return {
        probe: JSON.parse(wasm.probe_json(inputBytes)),
        summary: null,
        output: null,
      };
    case "summary":
      return {
        probe: null,
        summary: JSON.parse(wasm.summary_json(inputBytes)),
        output: null,
      };
    case "roundtrip": {
      const roundtripResult = wasm.roundtrip(inputBytes, config.prettyOutput);
      return {
        probe: null,
        summary: JSON.parse(roundtripResult.summaryJson()),
        output: Buffer.from(roundtripResult.outputBytes()),
      };
    }
    default:
      throw new Error(`unsupported operation: ${config.operation}`);
  }
}

function parseArgs(args) {
  let operation = null;
  let input = null;
  let iterations = null;
  let warmup = null;
  let output = null;
  let prettyOutput = false;
  let resultJson = null;

  for (let index = 0; index < args.length; index += 1) {
    const flag = args[index];
    switch (flag) {
      case "--operation":
        operation = takeValue(args, ++index, "--operation");
        break;
      case "--input":
        input = takeValue(args, ++index, "--input");
        break;
      case "--iterations":
        iterations = parseInteger(takeValue(args, ++index, "--iterations"), "--iterations");
        break;
      case "--warmup":
        warmup = parseInteger(takeValue(args, ++index, "--warmup"), "--warmup");
        break;
      case "--output":
        output = takeValue(args, ++index, "--output");
        break;
      case "--pretty-output":
        prettyOutput = true;
        break;
      case "--result-json":
        resultJson = takeValue(args, ++index, "--result-json");
        break;
      case "--help":
      case "-h":
        throw new Error(usage());
      default:
        throw new Error(`unknown argument: ${flag}\n\n${usage()}`);
    }
  }

  if (!["probe", "summary", "roundtrip"].includes(operation)) {
    throw new Error(`unsupported or missing --operation\n\n${usage()}`);
  }

  if (input === null || iterations === null || warmup === null || output === null || resultJson === null) {
    throw new Error(usage());
  }

  return {
    operation,
    input,
    iterations,
    warmup,
    output,
    prettyOutput,
    resultJson,
  };
}

function takeValue(args, index, flag) {
  const value = args[index];
  if (value === undefined) {
    throw new Error(`missing value for ${flag}\n\n${usage()}`);
  }
  return value;
}

function parseInteger(value, flag) {
  const parsed = Number.parseInt(value, 10);
  if (!Number.isSafeInteger(parsed) || parsed < 0) {
    throw new Error(`invalid integer for ${flag}: ${value}`);
  }
  return parsed;
}

function usage() {
  return (
    "usage: cjbench-wasm --operation {probe,summary,roundtrip} --input PATH " +
    "--iterations N --warmup N --output PATH --result-json PATH [--pretty-output]"
  );
}

try {
  main();
} catch (error) {
  const message = error instanceof Error ? error.message : String(error);
  process.stderr.write(`${message}\n`);
  process.exitCode = 1;
}
