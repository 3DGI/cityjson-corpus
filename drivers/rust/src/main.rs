use std::env;
use std::fmt::{Display, Formatter};
use std::fs;
use std::path::PathBuf;
use std::process::ExitCode;
use std::time::Instant;

use cjlib::{CityModel, json};
use serde::Serialize;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum Operation {
    Probe,
    Summary,
    Roundtrip,
}

impl Operation {
    fn parse(value: &str) -> Result<Self, String> {
        match value {
            "probe" => Ok(Self::Probe),
            "summary" => Ok(Self::Summary),
            "roundtrip" => Ok(Self::Roundtrip),
            _ => Err(format!("unsupported operation: {value}")),
        }
    }
}

impl Display for Operation {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Probe => write!(f, "probe"),
            Self::Summary => write!(f, "summary"),
            Self::Roundtrip => write!(f, "roundtrip"),
        }
    }
}

#[derive(Debug)]
struct Config {
    operation: Operation,
    input: PathBuf,
    iterations: usize,
    warmup: usize,
    output: PathBuf,
    pretty_output: bool,
    result_json: PathBuf,
}

#[derive(Debug, Clone, Serialize)]
struct ProbeMetrics {
    root_kind: String,
    version: Option<String>,
}

#[derive(Debug, Clone, Serialize)]
struct SummaryMetrics {
    model_type: String,
    version: Option<String>,
    cityobject_count: usize,
    geometry_count: usize,
    vertex_count: usize,
    template_vertex_count: usize,
    material_count: usize,
    texture_count: usize,
}

#[derive(Debug, Clone, Serialize)]
struct BenchmarkResult {
    target: &'static str,
    operation: String,
    input: String,
    input_bytes: usize,
    iterations: usize,
    warmup: usize,
    pretty_output: bool,
    samples_ns: Vec<u128>,
    output_bytes: Option<usize>,
    probe: Option<ProbeMetrics>,
    summary: Option<SummaryMetrics>,
}

#[derive(Debug, Clone)]
struct OperationOutcome {
    probe: Option<ProbeMetrics>,
    summary: Option<SummaryMetrics>,
    output: Option<Vec<u8>>,
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("{error}");
            ExitCode::FAILURE
        }
    }
}

fn run() -> Result<(), String> {
    let config = parse_args(env::args().skip(1))?;
    let input_bytes =
        fs::read(&config.input).map_err(|error| format!("failed to read input file: {error}"))?;

    for _ in 0..config.warmup {
        let _ = execute(&config, &input_bytes)?;
    }

    let mut samples_ns = Vec::with_capacity(config.iterations);
    let mut last_outcome = None;
    for _ in 0..config.iterations {
        let started = Instant::now();
        let outcome = execute(&config, &input_bytes)?;
        samples_ns.push(started.elapsed().as_nanos());
        last_outcome = Some(outcome);
    }

    let artifact_outcome = if config.operation == Operation::Roundtrip {
        let outcome = execute(&config, &input_bytes)?;
        let output = outcome.output.as_ref().ok_or_else(|| {
            "roundtrip did not produce output bytes while writing artifact".to_string()
        })?;
        fs::write(&config.output, output)
            .map_err(|error| format!("failed to write roundtrip output: {error}"))?;
        Some(outcome)
    } else {
        None
    };

    let result = build_result(
        &config,
        &input_bytes,
        samples_ns,
        artifact_outcome.or(last_outcome).ok_or_else(|| "no benchmark outcome".to_string())?,
    );

    let result_bytes = serde_json::to_vec_pretty(&result)
        .map_err(|error| format!("failed to serialize result json: {error}"))?;
    if let Some(parent) = config.result_json.parent() {
        fs::create_dir_all(parent)
            .map_err(|error| format!("failed to create result directory: {error}"))?;
    }
    fs::write(&config.result_json, result_bytes)
        .map_err(|error| format!("failed to write result json: {error}"))?;

    Ok(())
}

fn execute(config: &Config, input_bytes: &[u8]) -> Result<OperationOutcome, String> {
    match config.operation {
        Operation::Probe => {
            let probe = json::probe(input_bytes).map_err(|error| format!("probe failed: {error}"))?;
            Ok(OperationOutcome {
                probe: Some(ProbeMetrics {
                    root_kind: probe.kind().to_string(),
                    version: probe.version().map(|version| version.to_string()),
                }),
                summary: None,
                output: None,
            })
        }
        Operation::Summary => {
            let model = CityModel::from_slice(input_bytes)
                .map_err(|error| format!("summary parse failed: {error}"))?;
            Ok(OperationOutcome {
                probe: None,
                summary: Some(model_summary(&model)),
                output: None,
            })
        }
        Operation::Roundtrip => {
            let model = CityModel::from_slice(input_bytes)
                .map_err(|error| format!("roundtrip parse failed: {error}"))?;
            let summary = model_summary(&model);
            let output = json::to_vec_with_options(
                &model,
                json::WriteOptions {
                    pretty: config.pretty_output,
                    validate_default_themes: true,
                },
            )
            .map_err(|error| format!("roundtrip serialize failed: {error}"))?;
            Ok(OperationOutcome {
                probe: None,
                summary: Some(summary),
                output: Some(output),
            })
        }
    }
}

fn model_summary(model: &CityModel) -> SummaryMetrics {
    let inner = model.as_inner();
    SummaryMetrics {
        model_type: inner.type_citymodel().to_string(),
        version: inner.version().map(|version| version.to_string()),
        cityobject_count: inner.cityobjects().len(),
        geometry_count: inner.geometry_count(),
        vertex_count: inner.vertices().len(),
        template_vertex_count: inner.template_vertices().len(),
        material_count: inner.material_count(),
        texture_count: inner.texture_count(),
    }
}

fn build_result(
    config: &Config,
    input_bytes: &[u8],
    samples_ns: Vec<u128>,
    outcome: OperationOutcome,
) -> BenchmarkResult {
    BenchmarkResult {
        target: "rust",
        operation: config.operation.to_string(),
        input: config.input.display().to_string(),
        input_bytes: input_bytes.len(),
        iterations: config.iterations,
        warmup: config.warmup,
        pretty_output: config.pretty_output,
        samples_ns,
        output_bytes: outcome.output.as_ref().map(Vec::len),
        probe: outcome.probe,
        summary: outcome.summary,
    }
}

fn parse_args(args: impl Iterator<Item = String>) -> Result<Config, String> {
    let mut operation = None;
    let mut input = None;
    let mut iterations = None;
    let mut warmup = None;
    let mut output = None;
    let mut pretty_output = false;
    let mut result_json = None;

    let mut pending = args.peekable();
    while let Some(flag) = pending.next() {
        match flag.as_str() {
            "--operation" => operation = Some(parse_value(&mut pending, "--operation")?),
            "--input" => input = Some(PathBuf::from(parse_value(&mut pending, "--input")?)),
            "--iterations" => {
                iterations = Some(parse_usize(parse_value(&mut pending, "--iterations")?, "--iterations")?)
            }
            "--warmup" => warmup = Some(parse_usize(parse_value(&mut pending, "--warmup")?, "--warmup")?),
            "--output" => output = Some(PathBuf::from(parse_value(&mut pending, "--output")?)),
            "--pretty-output" => pretty_output = true,
            "--result-json" => {
                result_json = Some(PathBuf::from(parse_value(&mut pending, "--result-json")?))
            }
            "--help" | "-h" => return Err(usage()),
            other => return Err(format!("unknown argument: {other}\n\n{}", usage())),
        }
    }

    let operation =
        Operation::parse(&operation.ok_or_else(usage)?).map_err(|error| format!("{error}\n\n{}", usage()))?;

    Ok(Config {
        operation,
        input: input.ok_or_else(usage)?,
        iterations: iterations.ok_or_else(usage)?,
        warmup: warmup.ok_or_else(usage)?,
        output: output.ok_or_else(usage)?,
        pretty_output,
        result_json: result_json.ok_or_else(usage)?,
    })
}

fn parse_value(
    args: &mut std::iter::Peekable<impl Iterator<Item = String>>,
    flag: &str,
) -> Result<String, String> {
    args.next()
        .ok_or_else(|| format!("missing value for {flag}\n\n{}", usage()))
}

fn parse_usize(value: String, flag: &str) -> Result<usize, String> {
    value
        .parse::<usize>()
        .map_err(|error| format!("invalid integer for {flag}: {error}"))
}

fn usage() -> String {
    "usage: rust-driver --operation {probe,summary,roundtrip} --input PATH --iterations N --warmup N --output PATH --result-json PATH [--pretty-output]".to_string()
}
