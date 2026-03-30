use cjlib_wasm::{
    WriteOptions, parse_document_summary, probe_bytes, serialize_document_with_options,
};
use serde::Serialize;
use wasm_bindgen::prelude::*;

#[derive(Debug, Clone, Serialize)]
struct ProbeMetrics {
    root_kind: String,
    version: String,
    has_version: bool,
}

#[derive(Debug, Clone, Serialize)]
struct SummaryMetrics {
    model_type: String,
    version: String,
    cityobject_count: usize,
    geometry_count: usize,
    vertex_count: usize,
    template_vertex_count: usize,
    material_count: usize,
    texture_count: usize,
}

#[wasm_bindgen]
pub struct RoundtripResult {
    summary_json: String,
    output_bytes: Vec<u8>,
}

#[wasm_bindgen]
impl RoundtripResult {
    #[wasm_bindgen(js_name = summaryJson)]
    pub fn summary_json(&self) -> String {
        self.summary_json.clone()
    }

    #[wasm_bindgen(js_name = outputBytes)]
    pub fn output_bytes(&self) -> Vec<u8> {
        self.output_bytes.clone()
    }
}

#[wasm_bindgen]
pub fn probe_json(input_bytes: &[u8]) -> Result<String, JsValue> {
    let probe = probe_bytes(input_bytes).map_err(|error| wasm_error("probe failed", error))?;
    serialize_json(&ProbeMetrics {
        root_kind: format!("{:?}", probe.root_kind),
        version: format!("{:?}", probe.version),
        has_version: probe.has_version,
    })
}

#[wasm_bindgen]
pub fn summary_json(input_bytes: &[u8]) -> Result<String, JsValue> {
    let summary =
        parse_document_summary(input_bytes).map_err(|error| wasm_error("summary failed", error))?;
    serialize_json(&SummaryMetrics {
        model_type: format!("{:?}", summary.summary.model_type),
        version: format!("{:?}", summary.summary.version),
        cityobject_count: summary.summary.cityobject_count,
        geometry_count: summary.summary.geometry_count,
        vertex_count: summary.summary.vertex_count,
        template_vertex_count: summary.summary.template_vertex_count,
        material_count: summary.summary.material_count,
        texture_count: summary.summary.texture_count,
    })
}

#[wasm_bindgen]
pub fn roundtrip(input_bytes: &[u8], pretty_output: bool) -> Result<RoundtripResult, JsValue> {
    let summary = parse_document_summary(input_bytes)
        .map_err(|error| wasm_error("roundtrip summary failed", error))?;
    let output_bytes = serialize_document_with_options(
        input_bytes,
        WriteOptions {
            pretty: pretty_output,
            validate_default_themes: true,
        },
    )
    .map_err(|error| wasm_error("roundtrip serialize failed", error))?;

    Ok(RoundtripResult {
        summary_json: serialize_json(&SummaryMetrics {
            model_type: format!("{:?}", summary.summary.model_type),
            version: format!("{:?}", summary.summary.version),
            cityobject_count: summary.summary.cityobject_count,
            geometry_count: summary.summary.geometry_count,
            vertex_count: summary.summary.vertex_count,
            template_vertex_count: summary.summary.template_vertex_count,
            material_count: summary.summary.material_count,
            texture_count: summary.summary.texture_count,
        })?,
        output_bytes,
    })
}

fn serialize_json<T: Serialize>(value: &T) -> Result<String, JsValue> {
    serde_json::to_string(value).map_err(|error| {
        JsValue::from_str(&format!("failed to serialize wasm driver payload: {error}"))
    })
}

fn wasm_error(context: &str, error: cjlib_wasm::WasmError) -> JsValue {
    JsValue::from_str(&format!(
        "{context}: {} ({:?})",
        error.message, error.status
    ))
}
