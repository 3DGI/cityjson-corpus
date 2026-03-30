use std::fs;
use std::path::PathBuf;
use std::str::FromStr;

use cityjson::prelude::OwnedStringStorage;
use cityjson::v2_0::{CityObjectType, GeometryType, LoD};
use cjfake::cli::{
    AttributeConfig, CJFakeConfig, CityObjectConfig, GeometryConfig, MaterialConfig,
    MetadataConfig, SemanticConfig, TemplateConfig, TextureConfig, VertexConfig,
};
use serde::Deserialize;

#[derive(Deserialize, Default)]
#[serde(default)]
struct SyntheticProfile {
    cityobjects: CityObjectProfile,
    geometry: GeometryProfile,
    vertices: VertexProfile,
    materials: MaterialProfile,
    textures: TextureProfile,
    templates: TemplateGenerationProfile,
    metadata: MetadataProfile,
    attributes: AttributeProfile,
    semantics: SemanticProfile,
}

#[derive(Deserialize)]
#[serde(default)]
struct CityObjectProfile {
    allowed_types_cityobject: Option<Vec<String>>,
    min_cityobjects: u32,
    max_cityobjects: u32,
    cityobject_hierarchy: bool,
    min_children: u32,
    max_children: u32,
}

impl Default for CityObjectProfile {
    fn default() -> Self {
        Self {
            allowed_types_cityobject: None,
            min_cityobjects: 1,
            max_cityobjects: 1,
            cityobject_hierarchy: false,
            min_children: 1,
            max_children: 3,
        }
    }
}

#[derive(Deserialize)]
#[serde(default)]
struct GeometryProfile {
    allowed_types_geometry: Option<Vec<String>>,
    allowed_lods: Option<Vec<String>>,
    min_members_multipoint: u32,
    max_members_multipoint: u32,
    min_members_multilinestring: u32,
    max_members_multilinestring: u32,
    min_members_multisurface: u32,
    max_members_multisurface: u32,
    min_members_solid: u32,
    max_members_solid: u32,
    min_members_multisolid: u32,
    max_members_multisolid: u32,
    min_members_compositesurface: u32,
    max_members_compositesurface: u32,
    min_members_compositesolid: u32,
    max_members_compositesolid: u32,
    min_members_cityobject_geometries: u32,
    max_members_cityobject_geometries: u32,
}

impl Default for GeometryProfile {
    fn default() -> Self {
        Self {
            allowed_types_geometry: None,
            allowed_lods: None,
            min_members_multipoint: 11,
            max_members_multipoint: 11,
            min_members_multilinestring: 1,
            max_members_multilinestring: 1,
            min_members_multisurface: 1,
            max_members_multisurface: 1,
            min_members_solid: 1,
            max_members_solid: 3,
            min_members_multisolid: 1,
            max_members_multisolid: 3,
            min_members_compositesurface: 1,
            max_members_compositesurface: 3,
            min_members_compositesolid: 1,
            max_members_compositesolid: 3,
            min_members_cityobject_geometries: 1,
            max_members_cityobject_geometries: 1,
        }
    }
}

#[derive(Deserialize)]
#[serde(default)]
struct VertexProfile {
    min_coordinate: f64,
    max_coordinate: f64,
    min_vertices: u32,
    max_vertices: u32,
}

impl Default for VertexProfile {
    fn default() -> Self {
        Self {
            min_coordinate: -1000.0,
            max_coordinate: 1000.0,
            min_vertices: 8,
            max_vertices: 8,
        }
    }
}

#[derive(Deserialize)]
#[serde(default)]
struct MaterialProfile {
    materials_enabled: bool,
    min_materials: u32,
    max_materials: u32,
    nr_themes_materials: u32,
    generate_ambient_intensity: Option<bool>,
    generate_diffuse_color: Option<bool>,
    generate_emissive_color: Option<bool>,
    generate_specular_color: Option<bool>,
    generate_shininess: Option<bool>,
    generate_transparency: Option<bool>,
}

impl Default for MaterialProfile {
    fn default() -> Self {
        Self {
            materials_enabled: true,
            min_materials: 1,
            max_materials: 3,
            nr_themes_materials: 3,
            generate_ambient_intensity: None,
            generate_diffuse_color: None,
            generate_emissive_color: None,
            generate_specular_color: None,
            generate_shininess: None,
            generate_transparency: None,
        }
    }
}

#[derive(Deserialize)]
#[serde(default)]
struct TextureProfile {
    textures_enabled: bool,
    min_textures: u32,
    max_textures: u32,
    nr_themes_textures: u32,
    max_vertices_texture: u32,
    texture_allow_none: bool,
}

impl Default for TextureProfile {
    fn default() -> Self {
        Self {
            textures_enabled: true,
            min_textures: 2,
            max_textures: 2,
            nr_themes_textures: 3,
            max_vertices_texture: 10,
            texture_allow_none: false,
        }
    }
}

#[derive(Deserialize)]
#[serde(default)]
struct TemplateGenerationProfile {
    #[serde(alias = "use_templates")]
    enabled: bool,
    #[serde(alias = "min_templates")]
    min_count: u32,
    #[serde(alias = "max_templates")]
    max_count: u32,
}

impl Default for TemplateGenerationProfile {
    fn default() -> Self {
        Self {
            enabled: false,
            min_count: 1,
            max_count: 10,
        }
    }
}

#[derive(Deserialize)]
#[serde(default)]
#[allow(clippy::struct_excessive_bools)]
struct MetadataProfile {
    metadata_enabled: bool,
    metadata_geographical_extent: bool,
    metadata_identifier: bool,
    metadata_reference_date: bool,
    metadata_reference_system: bool,
    metadata_title: bool,
    metadata_point_of_contact: bool,
}

impl Default for MetadataProfile {
    fn default() -> Self {
        Self {
            metadata_enabled: true,
            metadata_geographical_extent: true,
            metadata_identifier: true,
            metadata_reference_date: true,
            metadata_reference_system: true,
            metadata_title: true,
            metadata_point_of_contact: true,
        }
    }
}

#[derive(Deserialize)]
#[serde(default)]
struct AttributeProfile {
    attributes_enabled: bool,
    min_attributes: u32,
    max_attributes: u32,
    attributes_max_depth: u8,
    attributes_random_keys: bool,
    attributes_random_values: bool,
}

impl Default for AttributeProfile {
    fn default() -> Self {
        Self {
            attributes_enabled: true,
            min_attributes: 3,
            max_attributes: 8,
            attributes_max_depth: 2,
            attributes_random_keys: true,
            attributes_random_values: true,
        }
    }
}

#[derive(Deserialize)]
#[serde(default)]
struct SemanticProfile {
    semantics_enabled: bool,
}

impl Default for SemanticProfile {
    fn default() -> Self {
        Self {
            semantics_enabled: true,
        }
    }
}

impl SyntheticProfile {
    fn into_config(self) -> CJFakeConfig {
        CJFakeConfig {
            cityobjects: self.cityobjects.into_config(),
            geometry: self.geometry.into_config(),
            vertices: self.vertices.into_config(),
            materials: self.materials.into_config(),
            textures: self.textures.into_config(),
            templates: self.templates.into_config(),
            metadata: self.metadata.into_config(),
            attributes: self.attributes.into_config(),
            semantics: self.semantics.into_config(),
            ..CJFakeConfig::default()
        }
    }
}

impl CityObjectProfile {
    fn into_config(self) -> CityObjectConfig {
        CityObjectConfig {
            allowed_types_cityobject: self.allowed_types_cityobject.map(|types| {
                types
                    .into_iter()
                    .map(|value| CityObjectType::<OwnedStringStorage>::from_str(&value).unwrap())
                    .collect()
            }),
            min_cityobjects: self.min_cityobjects,
            max_cityobjects: self.max_cityobjects,
            cityobject_hierarchy: self.cityobject_hierarchy,
            min_children: self.min_children,
            max_children: self.max_children,
        }
    }
}

impl GeometryProfile {
    fn into_config(self) -> GeometryConfig {
        GeometryConfig {
            allowed_types_geometry: self.allowed_types_geometry.map(|types| {
                types
                    .into_iter()
                    .map(|value| GeometryType::from_str(&value).unwrap())
                    .collect()
            }),
            allowed_lods: self
                .allowed_lods
                .map(|values| values.into_iter().map(|value| parse_lod(&value)).collect()),
            min_members_multipoint: self.min_members_multipoint,
            max_members_multipoint: self.max_members_multipoint,
            min_members_multilinestring: self.min_members_multilinestring,
            max_members_multilinestring: self.max_members_multilinestring,
            min_members_multisurface: self.min_members_multisurface,
            max_members_multisurface: self.max_members_multisurface,
            min_members_solid: self.min_members_solid,
            max_members_solid: self.max_members_solid,
            min_members_multisolid: self.min_members_multisolid,
            max_members_multisolid: self.max_members_multisolid,
            min_members_compositesurface: self.min_members_compositesurface,
            max_members_compositesurface: self.max_members_compositesurface,
            min_members_compositesolid: self.min_members_compositesolid,
            max_members_compositesolid: self.max_members_compositesolid,
            min_members_cityobject_geometries: self.min_members_cityobject_geometries,
            max_members_cityobject_geometries: self.max_members_cityobject_geometries,
        }
    }
}

impl VertexProfile {
    fn into_config(self) -> VertexConfig {
        VertexConfig {
            min_coordinate: self.min_coordinate,
            max_coordinate: self.max_coordinate,
            min_vertices: self.min_vertices,
            max_vertices: self.max_vertices,
        }
    }
}

impl MaterialProfile {
    fn into_config(self) -> MaterialConfig {
        MaterialConfig {
            materials_enabled: self.materials_enabled,
            min_materials: self.min_materials,
            max_materials: self.max_materials,
            nr_themes_materials: self.nr_themes_materials,
            generate_ambient_intensity: self.generate_ambient_intensity,
            generate_diffuse_color: self.generate_diffuse_color,
            generate_emissive_color: self.generate_emissive_color,
            generate_specular_color: self.generate_specular_color,
            generate_shininess: self.generate_shininess,
            generate_transparency: self.generate_transparency,
        }
    }
}

impl TextureProfile {
    fn into_config(self) -> TextureConfig {
        TextureConfig {
            textures_enabled: self.textures_enabled,
            min_textures: self.min_textures,
            max_textures: self.max_textures,
            nr_themes_textures: self.nr_themes_textures,
            max_vertices_texture: self.max_vertices_texture,
            texture_allow_none: self.texture_allow_none,
        }
    }
}

impl TemplateGenerationProfile {
    fn into_config(self) -> TemplateConfig {
        TemplateConfig {
            use_templates: self.enabled,
            min_templates: self.min_count,
            max_templates: self.max_count,
        }
    }
}

impl MetadataProfile {
    fn into_config(self) -> MetadataConfig {
        MetadataConfig {
            metadata_enabled: self.metadata_enabled,
            metadata_geographical_extent: self.metadata_geographical_extent,
            metadata_identifier: self.metadata_identifier,
            metadata_reference_date: self.metadata_reference_date,
            metadata_reference_system: self.metadata_reference_system,
            metadata_title: self.metadata_title,
            metadata_point_of_contact: self.metadata_point_of_contact,
        }
    }
}

impl AttributeProfile {
    fn into_config(self) -> AttributeConfig {
        AttributeConfig {
            attributes_enabled: self.attributes_enabled,
            min_attributes: self.min_attributes,
            max_attributes: self.max_attributes,
            attributes_max_depth: self.attributes_max_depth,
            attributes_random_keys: self.attributes_random_keys,
            attributes_random_values: self.attributes_random_values,
        }
    }
}

impl SemanticProfile {
    fn into_config(self) -> SemanticConfig {
        SemanticConfig {
            semantics_enabled: self.semantics_enabled,
            allowed_types_semantic: None,
        }
    }
}

fn parse_lod(value: &str) -> LoD {
    match value {
        "0" => LoD::LoD0,
        "0.0" => LoD::LoD0_0,
        "0.1" => LoD::LoD0_1,
        "0.2" => LoD::LoD0_2,
        "0.3" => LoD::LoD0_3,
        "1" => LoD::LoD1,
        "1.0" => LoD::LoD1_0,
        "1.1" => LoD::LoD1_1,
        "1.2" => LoD::LoD1_2,
        "1.3" => LoD::LoD1_3,
        "2" => LoD::LoD2,
        "2.0" => LoD::LoD2_0,
        "2.1" => LoD::LoD2_1,
        "2.2" => LoD::LoD2_2,
        "2.3" => LoD::LoD2_3,
        "3" => LoD::LoD3,
        "3.0" => LoD::LoD3_0,
        "3.1" => LoD::LoD3_1,
        "3.2" => LoD::LoD3_2,
        "3.3" => LoD::LoD3_3,
        _ => panic!("unknown LoD: {value}"),
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut args = std::env::args_os().skip(1);
    let profile_path = PathBuf::from(args.next().ok_or("missing profile path")?);
    let seed = args
        .next()
        .ok_or("missing seed")?
        .into_string()
        .map_err(|_| "seed must be valid utf-8")?
        .parse::<u64>()?;
    let output_path = PathBuf::from(args.next().ok_or("missing output path")?);

    let profile = serde_json::from_str::<SyntheticProfile>(&fs::read_to_string(&profile_path)?)?;
    let output = cjfake::generate_string(profile.into_config(), Some(seed))?;
    fs::write(output_path, output)?;
    Ok(())
}
