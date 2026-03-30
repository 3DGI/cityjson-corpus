#include <charconv>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <optional>
#include <sstream>
#include <stdexcept>
#include <system_error>
#include <string>
#include <string_view>
#include <vector>

#include <cjlib/cjlib.hpp>

namespace {

enum class Operation { kProbe, kSummary, kRoundtrip };

struct Args final {
  Operation operation;
  std::filesystem::path input_path;
  std::size_t iterations;
  std::size_t warmup;
  std::filesystem::path output_path;
  bool has_output_path = false;
  bool pretty_output = false;
  std::filesystem::path result_json;
};

struct ProbeResult final {
  std::string root_kind;
  std::string version;
  bool has_version = false;
};

struct SummaryResult final {
  std::string model_type;
  std::string version;
  std::size_t cityobject_count = 0U;
  std::size_t geometry_count = 0U;
  std::size_t geometry_template_count = 0U;
  std::size_t vertex_count = 0U;
  std::size_t template_vertex_count = 0U;
  std::size_t uv_coordinate_count = 0U;
  std::size_t semantic_count = 0U;
  std::size_t material_count = 0U;
  std::size_t texture_count = 0U;
  std::size_t extension_count = 0U;
  bool has_metadata = false;
  bool has_transform = false;
  bool has_templates = false;
  bool has_appearance = false;
};

struct Result final {
  std::string language;
  std::string operation;
  std::string input;
  std::size_t iterations = 0U;
  std::size_t warmup = 0U;
  bool pretty_output = false;
  std::uint64_t total_ns = 0U;
  double per_iteration_ns = 0.0;
  std::vector<std::uint64_t> samples_ns;
  std::size_t input_bytes = 0U;
  std::size_t output_bytes = 0U;
  std::optional<ProbeResult> probe;
  std::optional<SummaryResult> summary;
  std::optional<std::string> output_path;
};

std::string escape_json(std::string_view value) {
  std::ostringstream out;
  out << '"';
  for (const char ch : value) {
    switch (ch) {
      case '\\':
        out << "\\\\";
        break;
      case '"':
        out << "\\\"";
        break;
      case '\b':
        out << "\\b";
        break;
      case '\f':
        out << "\\f";
        break;
      case '\n':
        out << "\\n";
        break;
      case '\r':
        out << "\\r";
        break;
      case '\t':
        out << "\\t";
        break;
      default:
        out << ch;
        break;
    }
  }
  out << '"';
  return out.str();
}

void write_key(std::ostream& out, std::string_view key) {
  out << escape_json(key) << ": ";
}

void write_probe(std::ostream& out, const ProbeResult& probe) {
  out << "{";
  write_key(out, "root_kind");
  out << escape_json(probe.root_kind) << ", ";
  write_key(out, "version");
  out << escape_json(probe.version) << ", ";
  write_key(out, "has_version");
  out << (probe.has_version ? "true" : "false");
  out << "}";
}

void write_summary(std::ostream& out, const SummaryResult& summary) {
  out << "{";
  write_key(out, "model_type");
  out << escape_json(summary.model_type) << ", ";
  write_key(out, "version");
  out << escape_json(summary.version) << ", ";
  write_key(out, "cityobject_count");
  out << summary.cityobject_count << ", ";
  write_key(out, "geometry_count");
  out << summary.geometry_count << ", ";
  write_key(out, "geometry_template_count");
  out << summary.geometry_template_count << ", ";
  write_key(out, "vertex_count");
  out << summary.vertex_count << ", ";
  write_key(out, "template_vertex_count");
  out << summary.template_vertex_count << ", ";
  write_key(out, "uv_coordinate_count");
  out << summary.uv_coordinate_count << ", ";
  write_key(out, "semantic_count");
  out << summary.semantic_count << ", ";
  write_key(out, "material_count");
  out << summary.material_count << ", ";
  write_key(out, "texture_count");
  out << summary.texture_count << ", ";
  write_key(out, "extension_count");
  out << summary.extension_count << ", ";
  write_key(out, "has_metadata");
  out << (summary.has_metadata ? "true" : "false") << ", ";
  write_key(out, "has_transform");
  out << (summary.has_transform ? "true" : "false") << ", ";
  write_key(out, "has_templates");
  out << (summary.has_templates ? "true" : "false") << ", ";
  write_key(out, "has_appearance");
  out << (summary.has_appearance ? "true" : "false");
  out << "}";
}

void write_samples(std::ostream& out, const std::vector<std::uint64_t>& samples) {
  out << "[";
  for (std::size_t index = 0; index < samples.size(); ++index) {
    if (index > 0U) {
      out << ", ";
    }
    out << samples[index];
  }
  out << "]";
}

void write_result_json(std::ostream& out, const Result& result) {
  out << "{";
  write_key(out, "language");
  out << escape_json(result.language) << ", ";
  write_key(out, "operation");
  out << escape_json(result.operation) << ", ";
  write_key(out, "input");
  out << escape_json(result.input) << ", ";
  write_key(out, "iterations");
  out << result.iterations << ", ";
  write_key(out, "warmup");
  out << result.warmup << ", ";
  write_key(out, "pretty_output");
  out << (result.pretty_output ? "true" : "false") << ", ";
  write_key(out, "timing_ns");
  out << "{";
  write_key(out, "total");
  out << result.total_ns << ", ";
  write_key(out, "per_iteration");
  out << result.per_iteration_ns;
  out << "}, ";
  write_key(out, "samples_ns");
  write_samples(out, result.samples_ns);
  out << ", ";
  write_key(out, "input_bytes");
  out << result.input_bytes << ", ";
  write_key(out, "output_bytes");
  out << result.output_bytes << ", ";
  write_key(out, "probe");
  if (result.probe.has_value()) {
    write_probe(out, *result.probe);
  } else {
    out << "null";
  }
  out << ", ";
  write_key(out, "summary");
  if (result.summary.has_value()) {
    write_summary(out, *result.summary);
  } else {
    out << "null";
  }
  out << ", ";
  write_key(out, "output_path");
  if (result.output_path.has_value()) {
    out << escape_json(*result.output_path);
  } else {
    out << "null";
  }
  out << "}";
}

std::vector<std::uint8_t> read_file_bytes(const std::filesystem::path& path) {
  std::ifstream input(path, std::ios::binary);
  if (!input) {
    throw std::runtime_error("failed to open input file: " + path.string());
  }

  return std::vector<std::uint8_t>(
      std::istreambuf_iterator<char>(input), std::istreambuf_iterator<char>());
}

void ensure_parent_directory(const std::filesystem::path& path) {
  const auto parent = path.parent_path();
  if (!parent.empty()) {
    std::filesystem::create_directories(parent);
  }
}

std::string to_string(cjlib::RootKind kind) {
  switch (kind) {
    case CJ_ROOT_KIND_CITY_JSON:
      return "CITY_JSON";
    case CJ_ROOT_KIND_CITY_JSON_FEATURE:
      return "CITY_JSON_FEATURE";
    default:
      return "UNKNOWN";
  }
}

std::string to_string(cjlib::Version version) {
  switch (version) {
    case CJ_VERSION_V1_0:
      return "V1_0";
    case CJ_VERSION_V1_1:
      return "V1_1";
    case CJ_VERSION_V2_0:
      return "V2_0";
    default:
      return "UNKNOWN";
  }
}

std::string to_string(cjlib::ModelType model_type) {
  switch (model_type) {
    case CJ_MODEL_TYPE_CITY_JSON:
      return "CITY_JSON";
    case CJ_MODEL_TYPE_CITY_JSON_FEATURE:
      return "CITY_JSON_FEATURE";
    default:
      return "UNKNOWN";
  }
}

std::string to_string(Operation operation) {
  switch (operation) {
    case Operation::kProbe:
      return "probe";
    case Operation::kSummary:
      return "summary";
    case Operation::kRoundtrip:
      return "roundtrip";
  }
  return "probe";
}

Operation parse_operation(std::string_view value) {
  if (value == "probe") {
    return Operation::kProbe;
  }
  if (value == "summary") {
    return Operation::kSummary;
  }
  if (value == "roundtrip") {
    return Operation::kRoundtrip;
  }
  throw std::runtime_error("unsupported operation: " + std::string(value));
}

std::size_t parse_size(std::string_view value, std::string_view flag_name) {
  std::size_t parsed = 0U;
  const auto result = std::from_chars(value.data(), value.data() + value.size(), parsed);
  if (result.ec != std::errc{} || result.ptr != value.data() + value.size()) {
    throw std::runtime_error("invalid value for " + std::string(flag_name) + ": " + std::string(value));
  }
  return parsed;
}

Args parse_args(int argc, char** argv) {
  Args args{};
  bool saw_operation = false;
  bool saw_input = false;
  bool saw_iterations = false;
  bool saw_warmup = false;
  bool saw_result_json = false;

  for (int index = 1; index < argc; ++index) {
    const std::string_view arg{argv[index]};
    if (arg == "--pretty-output") {
      args.pretty_output = true;
      continue;
    }

    if (index + 1 >= argc) {
      throw std::runtime_error("missing value for flag: " + std::string(arg));
    }

    const std::string_view value{argv[++index]};
    if (arg == "--operation") {
      args.operation = parse_operation(value);
      saw_operation = true;
    } else if (arg == "--input") {
      args.input_path = value;
      saw_input = true;
    } else if (arg == "--iterations") {
      args.iterations = parse_size(value, arg);
      saw_iterations = true;
    } else if (arg == "--warmup") {
      args.warmup = parse_size(value, arg);
      saw_warmup = true;
    } else if (arg == "--output") {
      args.output_path = value;
      args.has_output_path = true;
    } else if (arg == "--result-json") {
      args.result_json = value;
      saw_result_json = true;
    } else {
      throw std::runtime_error("unknown flag: " + std::string(arg));
    }
  }

  if (!saw_operation || !saw_input || !saw_iterations || !saw_warmup || !saw_result_json) {
    throw std::runtime_error("missing required arguments");
  }
  if (args.iterations == 0U) {
    throw std::runtime_error("--iterations must be greater than 0");
  }
  return args;
}

SummaryResult make_summary(const cjlib::ModelSummary& summary) {
  return SummaryResult{
      .model_type = to_string(summary.model_type),
      .version = to_string(summary.version),
      .cityobject_count = summary.cityobject_count,
      .geometry_count = summary.geometry_count,
      .geometry_template_count = summary.geometry_template_count,
      .vertex_count = summary.vertex_count,
      .template_vertex_count = summary.template_vertex_count,
      .uv_coordinate_count = summary.uv_coordinate_count,
      .semantic_count = summary.semantic_count,
      .material_count = summary.material_count,
      .texture_count = summary.texture_count,
      .extension_count = summary.extension_count,
      .has_metadata = summary.has_metadata,
      .has_transform = summary.has_transform,
      .has_templates = summary.has_templates,
      .has_appearance = summary.has_appearance,
  };
}

ProbeResult make_probe(const cjlib::Probe& probe) {
  return ProbeResult{
      .root_kind = to_string(probe.root_kind),
      .version = to_string(probe.version),
      .has_version = probe.has_version,
  };
}

}  // namespace

int main(int argc, char** argv) {
  try {
    const auto args = parse_args(argc, argv);
    if (args.operation == Operation::kRoundtrip && !args.has_output_path) {
      throw std::runtime_error("--output is required for roundtrip");
    }

    const auto payload = read_file_bytes(args.input_path);

    std::optional<ProbeResult> probe_result;
    std::optional<SummaryResult> summary_result;
    std::vector<std::uint8_t> output_payload;
    std::vector<std::uint64_t> samples_ns;
    samples_ns.reserve(args.iterations);

    for (std::size_t index = 0; index < args.warmup; ++index) {
      if (args.operation == Operation::kProbe) {
        static_cast<void>(cjlib::Model::probe(payload));
        continue;
      }

      auto model = cjlib::Model::parse_document(payload);
      if (args.operation == Operation::kSummary) {
        static_cast<void>(model.summary());
      } else {
        const auto serialized = model.serialize_document(cjlib::WriteOptions{
            .pretty = args.pretty_output,
            .validate_default_themes = true,
        });
        output_payload.assign(serialized.begin(), serialized.end());
      }
    }

    for (std::size_t index = 0; index < args.iterations; ++index) {
      const auto sample_start = std::chrono::steady_clock::now();
      if (args.operation == Operation::kProbe) {
        probe_result = make_probe(cjlib::Model::probe(payload));
      } else {
        auto model = cjlib::Model::parse_document(payload);
        summary_result = make_summary(model.summary());
        if (args.operation == Operation::kRoundtrip) {
          const auto serialized = model.serialize_document(cjlib::WriteOptions{
              .pretty = args.pretty_output,
              .validate_default_themes = true,
          });
          output_payload.assign(serialized.begin(), serialized.end());
        }
      }
      const auto sample_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(
                                 std::chrono::steady_clock::now() - sample_start)
                                 .count();
      samples_ns.push_back(static_cast<std::uint64_t>(sample_ns));
    }
    const auto elapsed_ns = std::accumulate(samples_ns.begin(), samples_ns.end(), std::uint64_t{0});

    if (args.operation == Operation::kRoundtrip) {
      ensure_parent_directory(args.output_path);
      std::ofstream output(args.output_path, std::ios::binary);
      if (!output) {
        throw std::runtime_error("failed to open output file: " + args.output_path.string());
      }
      output.write(reinterpret_cast<const char*>(output_payload.data()),
                   static_cast<std::streamsize>(output_payload.size()));
      if (!output) {
        throw std::runtime_error("failed to write output file: " + args.output_path.string());
      }
    }

    Result result{};
    result.language = "cpp";
    result.operation = to_string(args.operation);
    result.input = args.input_path.string();
    result.iterations = args.iterations;
    result.warmup = args.warmup;
    result.pretty_output = args.pretty_output;
    result.total_ns = elapsed_ns;
    result.per_iteration_ns = static_cast<double>(elapsed_ns) / static_cast<double>(samples_ns.size());
    result.samples_ns = std::move(samples_ns);
    result.input_bytes = payload.size();
    result.output_bytes = output_payload.size();
    result.probe = probe_result;
    result.summary = summary_result;
    if (args.has_output_path) {
      result.output_path = args.output_path.string();
    }

    ensure_parent_directory(args.result_json);
    std::ofstream result_json(args.result_json, std::ios::binary);
    if (!result_json) {
      throw std::runtime_error("failed to open result json file: " + args.result_json.string());
    }
    write_result_json(result_json, result);
    result_json << '\n';
    if (!result_json) {
      throw std::runtime_error("failed to write result json file: " + args.result_json.string());
    }

    return 0;
  } catch (const std::exception& error) {
    std::cerr << "error: " << error.what() << '\n';
    return 1;
  }
}
