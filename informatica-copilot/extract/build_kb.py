"""Turn parsed PowerCenter metadata into a Copilot-ready knowledge base.

Copilot retrieves *chunks*, not documents, so every generated file repeats the
mapping name and the folder in each section heading. A chunk that lands in the
model's context without those names cannot be attributed to a mapping and is
worse than no chunk at all.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import defaultdict

from parse_powercenter import (
    Mapping,
    Repository,
    Table,
    parse_directory,
    trace_lineage,
)

MAX_CHAIN_HOPS = 12


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "_None._\n"
    escaped = [[(cell or "").replace("|", "\\|").replace("\n", " ") for cell in row] for row in rows]
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join([" --- "] * len(headers)) + "|"]
    out += ["| " + " | ".join(row) + " |" for row in escaped]
    return "\n".join(out) + "\n"


def resolve_table(repo: Repository, mapping: Mapping, instance_name: str, kind: str) -> Table | None:
    for instance in mapping.instances_of(kind):
        if instance.name == instance_name:
            name = instance.transformation_name or instance.name
            return repo.table(mapping.folder, kind, name)
    return None


def expression_for(mapping: Mapping, instance: str, field_name: str) -> str:
    for candidate in mapping.instances:
        if candidate.name != instance:
            continue
        transformation = mapping.transformations.get(candidate.transformation_name or instance)
        if not transformation:
            return ""
        for port in transformation.fields:
            if port.name == field_name and port.expression:
                return port.expression
    return ""


def chain_summary(mapping: Mapping, chain: list[str]) -> tuple[str, str]:
    """Return (origin port, human readable hop path with any expressions)."""
    trimmed = chain if len(chain) <= MAX_CHAIN_HOPS else chain[:2] + ["…"] + chain[-3:]
    annotated = []
    for hop in trimmed:
        if hop in ("…", "<cycle>"):
            annotated.append(hop)
            continue
        instance, _, port = hop.rpartition(".")
        expression = expression_for(mapping, instance, port)
        annotated.append(f"{hop} = `{expression}`" if expression else hop)
    return chain[0], " → ".join(annotated)


def render_mapping(repo: Repository, mapping: Mapping) -> str:
    title = f"{mapping.name}"
    lines: list[str] = []
    lines.append(f"# Mapping {title}")
    lines.append("")
    lines.append(f"- **Mapping name:** {mapping.name}")
    lines.append(f"- **Folder:** {mapping.folder}")
    lines.append(f"- **Valid in repository:** {mapping.is_valid or 'unknown'}")
    lines.append(f"- **Exported from:** {mapping.source_file}")
    if mapping.description:
        lines.append(f"- **Description:** {mapping.description}")

    source_instances = mapping.instances_of("SOURCE")
    target_instances = mapping.instances_of("TARGET")
    source_names = ", ".join(i.name for i in source_instances) or "none"
    target_names = ", ".join(i.name for i in target_instances) or "none"
    lines.append(f"- **Sources:** {source_names}")
    lines.append(f"- **Targets:** {target_names}")
    lookups = sorted(
        {
            transformation.attributes["Lookup table name"]
            for transformation in mapping.transformations.values()
            if "Lookup table name" in transformation.attributes
        }
    )
    if lookups:
        lines.append(f"- **Lookup / reference tables:** {', '.join(lookups)}")
    lines.append("")
    lines.append(
        f"In one line: mapping {mapping.name} reads {source_names} and writes {target_names}."
    )
    lines.append("")

    lines.append(f"## Sources of mapping {title}")
    lines.append("")
    rows = []
    for instance in source_instances:
        table = resolve_table(repo, mapping, instance.name, "SOURCE")
        rows.append(
            [
                instance.name,
                table.qualified_name if table else instance.transformation_name,
                table.database_type if table else instance.transformation_type,
                table.dbd_name if table else "",
                str(len(table.fields)) if table else "?",
            ]
        )
    lines.append(md_table(["Instance", "Table", "Database type", "DBD / schema", "Columns"], rows))

    lines.append(f"## Targets of mapping {title}")
    lines.append("")
    rows = []
    order = {name: position for position, (position, name) in enumerate(mapping.target_load_order, 1)}
    for instance in target_instances:
        table = resolve_table(repo, mapping, instance.name, "TARGET")
        rows.append(
            [
                instance.name,
                table.qualified_name if table else instance.transformation_name,
                table.database_type if table else instance.transformation_type,
                str(order.get(instance.name, "")),
                str(len(table.fields)) if table else "?",
            ]
        )
    lines.append(md_table(["Instance", "Table", "Database type", "Load order", "Columns"], rows))

    lines.append(f"## Transformation logic in mapping {title}")
    lines.append("")
    pipeline_rows = []
    for instance in mapping.instances_of("TRANSFORMATION"):
        transformation = mapping.transformations.get(instance.transformation_name or instance.name)
        detail = ""
        if transformation:
            bits = [f"{k}: {v}" for k, v in transformation.attributes.items()]
            group_by = [p.name for p in transformation.fields if p.group_by]
            if group_by:
                bits.append("Group by: " + ", ".join(group_by))
            if transformation.group_names:
                bits.append("Groups: " + ", ".join(transformation.group_names))
            detail = "; ".join(bits)
        pipeline_rows.append(
            [
                instance.name,
                instance.transformation_type,
                "yes" if transformation and transformation.reusable else "no",
                detail,
            ]
        )
    lines.append(md_table(["Instance", "Type", "Reusable", "Configuration"], pipeline_rows))

    expressions = []
    for instance in mapping.instances_of("TRANSFORMATION"):
        transformation = mapping.transformations.get(instance.transformation_name or instance.name)
        if not transformation:
            continue
        for port in transformation.fields:
            if port.expression:
                expressions.append([instance.name, port.name, port.type_signature, port.expression])
    if expressions:
        lines.append(f"### Port expressions in mapping {title}")
        lines.append("")
        lines.append(md_table(["Instance", "Port", "Datatype", "Expression"], expressions))

    lines.append(f"## Column level lineage for mapping {title}")
    lines.append("")
    lines.append(
        "Each row answers: which source column ends up in this target column, and what "
        "happens to it on the way."
    )
    lines.append("")
    for instance in target_instances:
        table = resolve_table(repo, mapping, instance.name, "TARGET")
        lines.append(f"### Target {instance.name} in mapping {title}")
        lines.append("")
        rows = []
        target_fields = table.fields if table else []
        if not target_fields:
            fed = sorted({c.to_field for c in mapping.connectors if c.to_instance == instance.name})
            target_fields = [type("F", (), {"name": n, "type_signature": "", "nullable": "", "key_type": ""})() for n in fed]
        for target_field in target_fields:
            chains = trace_lineage(mapping, instance.name, target_field.name)
            fed_chains = [c for c in chains if len(c) > 1]
            if not fed_chains:
                rows.append([target_field.name, getattr(target_field, "type_signature", ""), "NOT CONNECTED", ""])
                continue
            for chain in fed_chains:
                origin, path = chain_summary(mapping, chain)
                rows.append([target_field.name, getattr(target_field, "type_signature", ""), origin, path])
        lines.append(
            md_table(["Target column", "Datatype", "Origin port", "Path (source → target)"], rows)
        )

    lines.append(f"## Full column lists for mapping {title}")
    lines.append("")
    for kind, instances in (("Source", source_instances), ("Target", target_instances)):
        for instance in instances:
            table = resolve_table(repo, mapping, instance.name, kind.upper())
            if not table:
                continue
            lines.append(f"### {kind} {instance.name} ({table.qualified_name}) columns")
            lines.append("")
            lines.append(
                md_table(
                    ["Column", "Datatype", "Nullable", "Key"],
                    [[f.name, f.type_signature, f.nullable, f.key_type] for f in table.fields],
                )
            )

    if mapping.sessions:
        lines.append(f"## Sessions and connections for mapping {title}")
        lines.append("")
        rows = []
        for session in mapping.sessions:
            for connection in session.connections:
                rows.append(
                    [
                        session.workflow,
                        session.name,
                        connection.get("instance", ""),
                        connection.get("role", ""),
                        connection.get("name", ""),
                        connection.get("subtype", ""),
                    ]
                )
            if not session.connections:
                rows.append([session.workflow, session.name, "", "", "", ""])
        lines.append(
            md_table(["Workflow", "Session", "Instance", "Role", "Connection", "Type"], rows)
        )

    return "\n".join(lines).rstrip() + "\n"


def render_table_card(repo: Repository, table: Table, usage: dict[str, list[str]]) -> str:
    lines = [f"# Table {table.qualified_name} ({table.kind.lower()} in folder {table.folder})", ""]
    lines.append(f"- **Table:** {table.qualified_name}")
    lines.append(f"- **Used as:** {table.kind.lower()}")
    lines.append(f"- **Folder:** {table.folder}")
    lines.append(f"- **Database type:** {table.database_type or 'unknown'}")
    lines.append(f"- **Column count:** {len(table.fields)}")
    lines.append("")
    lines.append(f"## Mappings that use {table.qualified_name}")
    lines.append("")
    reads = usage.get("reads", [])
    writes = usage.get("writes", [])
    lines.append(f"- Mappings reading it as a source: {', '.join(reads) or 'none'}")
    lines.append(f"- Mappings writing it as a target: {', '.join(writes) or 'none'}")
    lines.append("")
    lines.append(f"## Columns of {table.qualified_name}")
    lines.append("")
    lines.append(
        md_table(
            ["Column", "Datatype", "Nullable", "Key"],
            [[f.name, f.type_signature, f.nullable, f.key_type] for f in table.fields],
        )
    )
    return "\n".join(lines).rstrip() + "\n"


def build_usage(repo: Repository) -> dict[tuple[str, str], dict[str, list[str]]]:
    usage: dict[tuple[str, str], dict[str, list[str]]] = defaultdict(lambda: {"reads": [], "writes": []})
    for mapping in repo.mappings.values():
        for instance in mapping.instances_of("SOURCE"):
            key = (mapping.folder, instance.transformation_name or instance.name)
            usage[key]["reads"].append(mapping.name)
        for instance in mapping.instances_of("TARGET"):
            key = (mapping.folder, instance.transformation_name or instance.name)
            usage[key]["writes"].append(mapping.name)
    return usage


def render_index(repo: Repository) -> str:
    lines = ["# Informatica mapping catalogue", ""]
    lines.append(
        "One row per mapping. Use it to find the mapping name, then open that "
        "mapping's own page for columns, logic and lineage."
    )
    lines.append("")
    rows = []
    for (folder, name), mapping in sorted(repo.mappings.items()):
        rows.append(
            [
                name,
                folder,
                ", ".join(i.name for i in mapping.instances_of("SOURCE")),
                ", ".join(i.name for i in mapping.instances_of("TARGET")),
                ", ".join(sorted({s.workflow for s in mapping.sessions})),
            ]
        )
    lines.append(md_table(["Mapping", "Folder", "Sources", "Targets", "Workflows"], rows))
    return "\n".join(lines).rstrip() + "\n"


def mapping_to_dict(repo: Repository, mapping: Mapping) -> dict:
    def table_payload(instance_name: str, kind: str) -> dict:
        table = resolve_table(repo, mapping, instance_name, kind)
        return {
            "instance": instance_name,
            "table": table.qualified_name if table else instance_name,
            "database_type": table.database_type if table else "",
            "columns": [
                {"name": f.name, "datatype": f.type_signature, "nullable": f.nullable, "key": f.key_type}
                for f in (table.fields if table else [])
            ],
        }

    lineage = []
    for instance in mapping.instances_of("TARGET"):
        table = resolve_table(repo, mapping, instance.name, "TARGET")
        for target_field in table.fields if table else []:
            for chain in trace_lineage(mapping, instance.name, target_field.name):
                if len(chain) > 1:
                    lineage.append(
                        {
                            "target_instance": instance.name,
                            "target_column": target_field.name,
                            "origin": chain[0],
                            "path": chain,
                        }
                    )
    return {
        "name": mapping.name,
        "folder": mapping.folder,
        "description": mapping.description,
        "sources": [table_payload(i.name, "SOURCE") for i in mapping.instances_of("SOURCE")],
        "targets": [table_payload(i.name, "TARGET") for i in mapping.instances_of("TARGET")],
        "transformations": [
            {
                "instance": i.name,
                "type": i.transformation_type,
                "configuration": mapping.transformations.get(
                    i.transformation_name or i.name,
                    type("T", (), {"attributes": {}})(),
                ).attributes,
            }
            for i in mapping.instances_of("TRANSFORMATION")
        ],
        "lineage": lineage,
        "workflows": sorted({s.workflow for s in mapping.sessions}),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xml-dir", required=True, help="folder holding PowerCenter XML exports")
    parser.add_argument("--out-dir", required=True, help="folder to write the knowledge base into")
    args = parser.parse_args()

    try:
        repo = parse_directory(args.xml_dir)
    except FileNotFoundError as error:
        print(f"error: {error}")
        return 1
    usage = build_usage(repo)

    mappings_dir = os.path.join(args.out_dir, "mappings")
    tables_dir = os.path.join(args.out_dir, "tables")
    os.makedirs(mappings_dir, exist_ok=True)
    os.makedirs(tables_dir, exist_ok=True)

    for (folder, name), mapping in repo.mappings.items():
        path = os.path.join(mappings_dir, f"{slug(folder)}__{slug(name)}.md")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(render_mapping(repo, mapping))

    for (folder, kind, name), table in repo.tables.items():
        path = os.path.join(tables_dir, f"{slug(folder)}__{kind}__{slug(name)}.md")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(render_table_card(repo, table, usage.get((folder, name), {})))

    with open(os.path.join(args.out_dir, "00-mapping-catalogue.md"), "w", encoding="utf-8") as handle:
        handle.write(render_index(repo))

    payload = [mapping_to_dict(repo, m) for m in repo.mappings.values()]
    with open(os.path.join(args.out_dir, "mappings.json"), "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    print(
        f"parsed {len(repo.mappings)} mappings, {len(repo.tables)} tables, "
        f"{len(repo.workflows)} workflows -> {args.out_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
