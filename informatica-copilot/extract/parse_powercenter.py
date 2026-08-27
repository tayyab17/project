"""Parse Informatica PowerCenter repository XML exports into a normalised model.

Only the standard library is used so the script can run on a locked-down
corporate workstation where installing packages is not an option.
"""

from __future__ import annotations

import glob
import os
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Iterable

# Transformation attributes worth surfacing to a business user. Anything else in
# the export is engine plumbing (tracing level, partitioning, sort cache size).
INTERESTING_ATTRIBUTES = {
    "Sql Query",
    "Source Filter",
    "User Defined Join",
    "Filter Condition",
    "Join Condition",
    "Join Type",
    "Lookup Sql Override",
    "Lookup condition",
    "Lookup table name",
    "Lookup Source Filter",
    "Update Strategy Expression",
    "Sorter Key",
    "Sql Query Override",
    "Stored Procedure Name",
    "Sequence Name",
}


@dataclass
class Field:
    name: str
    datatype: str = ""
    precision: str = ""
    scale: str = ""
    nullable: str = ""
    key_type: str = ""
    port_type: str = ""
    expression: str = ""
    group_by: bool = False

    @property
    def type_signature(self) -> str:
        if not self.datatype:
            return ""
        # PowerCenter writes placeholder datatypes such as "number(p,s)"; the real
        # precision and scale live in their own attributes, so substitute them in.
        base = self.datatype
        if base.endswith("(p,s)"):
            base = base[: -len("(p,s)")]
        elif "(" in base:
            return base
        if self.scale and self.scale not in ("0", ""):
            return f"{base}({self.precision},{self.scale})"
        if self.precision:
            return f"{base}({self.precision})"
        return base


@dataclass
class Table:
    name: str
    kind: str  # SOURCE | TARGET
    database_type: str = ""
    owner: str = ""
    dbd_name: str = ""
    folder: str = ""
    fields: list[Field] = field(default_factory=list)

    @property
    def qualified_name(self) -> str:
        return f"{self.owner}.{self.name}" if self.owner else self.name


@dataclass
class Transformation:
    name: str
    type: str
    reusable: bool = False
    description: str = ""
    fields: list[Field] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)
    group_names: list[str] = field(default_factory=list)


@dataclass
class Instance:
    name: str
    type: str  # SOURCE | TARGET | TRANSFORMATION
    transformation_name: str = ""
    transformation_type: str = ""


@dataclass
class Connector:
    from_instance: str
    from_field: str
    to_instance: str
    to_field: str


@dataclass
class Mapping:
    name: str
    folder: str
    description: str = ""
    is_valid: str = ""
    instances: list[Instance] = field(default_factory=list)
    connectors: list[Connector] = field(default_factory=list)
    transformations: dict[str, Transformation] = field(default_factory=dict)
    target_load_order: list[tuple[str, str]] = field(default_factory=list)
    sessions: list["Session"] = field(default_factory=list)
    source_file: str = ""

    def instances_of(self, kind: str) -> list[Instance]:
        return [i for i in self.instances if i.type == kind]


@dataclass
class Session:
    name: str
    workflow: str
    mapping_name: str
    connections: list[dict[str, str]] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)


@dataclass
class Workflow:
    name: str
    folder: str
    scheduler: str = ""
    sessions: list[Session] = field(default_factory=list)
    links: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class Repository:
    tables: dict[tuple[str, str, str], Table] = field(default_factory=dict)
    mappings: dict[tuple[str, str], Mapping] = field(default_factory=dict)
    workflows: dict[tuple[str, str], Workflow] = field(default_factory=dict)

    def table(self, folder: str, kind: str, name: str) -> Table | None:
        return self.tables.get((folder, kind, name))


def _text(element: ET.Element, attr: str, default: str = "") -> str:
    return (element.get(attr) or default).strip()


def _parse_fields(parent: ET.Element, tags: Iterable[str]) -> list[Field]:
    fields: list[Field] = []
    for tag in tags:
        for node in parent.findall(tag):
            fields.append(
                Field(
                    name=_text(node, "NAME"),
                    datatype=_text(node, "DATATYPE"),
                    precision=_text(node, "PRECISION"),
                    scale=_text(node, "SCALE"),
                    nullable=_text(node, "NULLABLE"),
                    key_type=_text(node, "KEYTYPE"),
                    port_type=_text(node, "PORTTYPE"),
                    expression=_text(node, "EXPRESSION"),
                    group_by=_text(node, "GROUPBY").upper() == "YES",
                )
            )
    return fields


def _parse_table(node: ET.Element, kind: str, folder: str) -> Table:
    tag = "SOURCEFIELD" if kind == "SOURCE" else "TARGETFIELD"
    return Table(
        name=_text(node, "NAME"),
        kind=kind,
        database_type=_text(node, "DATABASETYPE"),
        owner=_text(node, "OWNERNAME"),
        dbd_name=_text(node, "DBDNAME"),
        folder=folder,
        fields=_parse_fields(node, [tag]),
    )


def _parse_transformation(node: ET.Element) -> Transformation:
    attributes = {}
    for attr in node.findall("TABLEATTRIBUTE"):
        name = _text(attr, "NAME")
        value = _text(attr, "VALUE")
        if value and name in INTERESTING_ATTRIBUTES:
            attributes[name] = value
    return Transformation(
        name=_text(node, "NAME"),
        type=_text(node, "TYPE"),
        reusable=_text(node, "REUSABLE").upper() == "YES",
        description=_text(node, "DESCRIPTION"),
        fields=_parse_fields(node, ["TRANSFORMFIELD"]),
        attributes=attributes,
        group_names=[_text(g, "NAME") for g in node.findall("GROUP")],
    )


def _parse_mapping(node: ET.Element, folder: str, source_file: str) -> Mapping:
    mapping = Mapping(
        name=_text(node, "NAME"),
        folder=folder,
        description=_text(node, "DESCRIPTION"),
        is_valid=_text(node, "ISVALID"),
        source_file=source_file,
    )
    for child in node.findall("TRANSFORMATION"):
        transformation = _parse_transformation(child)
        mapping.transformations[transformation.name] = transformation
    for child in node.findall("INSTANCE"):
        mapping.instances.append(
            Instance(
                name=_text(child, "NAME"),
                type=_text(child, "TYPE"),
                transformation_name=_text(child, "TRANSFORMATION_NAME"),
                transformation_type=_text(child, "TRANSFORMATION_TYPE"),
            )
        )
    for child in node.findall("CONNECTOR"):
        mapping.connectors.append(
            Connector(
                from_instance=_text(child, "FROMINSTANCE"),
                from_field=_text(child, "FROMFIELD"),
                to_instance=_text(child, "TOINSTANCE"),
                to_field=_text(child, "TOFIELD"),
            )
        )
    for child in node.findall("TARGETLOADORDER"):
        mapping.target_load_order.append(
            (_text(child, "ORDER"), _text(child, "TARGETINSTANCE"))
        )
    mapping.target_load_order.sort(key=lambda pair: int(pair[0] or 0))
    return mapping


def _parse_session(node: ET.Element, workflow_name: str) -> Session:
    session = Session(
        name=_text(node, "NAME"),
        workflow=workflow_name,
        mapping_name=_text(node, "MAPPINGNAME"),
    )
    for extension in node.iter("SESSIONEXTENSION"):
        instance = _text(extension, "SINSTANCENAME") or _text(extension, "NAME")
        role = _text(extension, "TYPE")
        for reference in extension.findall("CONNECTIONREFERENCE"):
            session.connections.append(
                {
                    "instance": instance,
                    "role": role,
                    "name": _text(reference, "CONNECTIONNAME"),
                    "type": _text(reference, "CONNECTIONTYPE"),
                    "subtype": _text(reference, "CONNECTIONSUBTYPE"),
                }
            )
    for attribute in node.findall("ATTRIBUTE"):
        name, value = _text(attribute, "NAME"), _text(attribute, "VALUE")
        if value:
            session.attributes[name] = value
    return session


def _parse_workflow(node: ET.Element, folder: str) -> Workflow:
    workflow = Workflow(name=_text(node, "NAME"), folder=folder)
    for scheduler in node.findall("SCHEDULER"):
        workflow.scheduler = _text(scheduler, "SCHEDULERNAME") or _text(scheduler, "NAME")
    for session_node in node.iter("SESSION"):
        workflow.sessions.append(_parse_session(session_node, workflow.name))
    for link in node.findall("WORKFLOWLINK"):
        workflow.links.append((_text(link, "FROMTASK"), _text(link, "TOTASK")))
    return workflow


def parse_file(path: str, repo: Repository) -> None:
    tree = ET.parse(path)
    root = tree.getroot()
    for folder_node in root.iter("FOLDER"):
        folder = _text(folder_node, "NAME")
        for source_node in folder_node.findall("SOURCE"):
            table = _parse_table(source_node, "SOURCE", folder)
            repo.tables[(folder, "SOURCE", table.name)] = table
        for target_node in folder_node.findall("TARGET"):
            table = _parse_table(target_node, "TARGET", folder)
            repo.tables[(folder, "TARGET", table.name)] = table
        for mapping_node in folder_node.findall("MAPPING"):
            mapping = _parse_mapping(mapping_node, folder, os.path.basename(path))
            repo.mappings[(folder, mapping.name)] = mapping
        for workflow_node in folder_node.findall("WORKFLOW"):
            workflow = _parse_workflow(workflow_node, folder)
            repo.workflows[(folder, workflow.name)] = workflow

    # Sessions live under workflows but describe a mapping, so attach them after
    # every folder is loaded — a workflow may reference a mapping parsed later.
    for workflow in repo.workflows.values():
        for session in workflow.sessions:
            mapping = repo.mappings.get((workflow.folder, session.mapping_name))
            if mapping and session not in mapping.sessions:
                mapping.sessions.append(session)


def parse_directory(xml_dir: str) -> Repository:
    repo = Repository()
    paths = sorted(glob.glob(os.path.join(xml_dir, "**", "*.xml"), recursive=True))
    if not paths:
        raise FileNotFoundError(f"no .xml files found under {xml_dir}")
    for path in paths:
        parse_file(path, repo)
    return repo


def trace_lineage(mapping: Mapping, instance: str, field_name: str) -> list[list[str]]:
    """Walk connectors backwards from one port to every upstream source port.

    Returns a list of hop chains, each ordered source-first. A port fed by a
    router or a joiner legitimately has several upstream chains.
    """
    incoming: dict[tuple[str, str], list[tuple[str, str]]] = defaultdict(list)
    for connector in mapping.connectors:
        incoming[(connector.to_instance, connector.to_field)].append(
            (connector.from_instance, connector.from_field)
        )

    source_instances = {i.name for i in mapping.instances_of("SOURCE")}
    chains: list[list[str]] = []

    def walk(node: tuple[str, str], path: list[str], seen: set[tuple[str, str]]) -> None:
        label = f"{node[0]}.{node[1]}"
        path = [label] + path
        if node in seen:
            chains.append(["<cycle>"] + path)
            return
        parents = incoming.get(node)
        if not parents or node[0] in source_instances:
            chains.append(path)
            return
        seen = seen | {node}
        for parent in parents:
            walk(parent, path, seen)

    walk((instance, field_name), [], set())
    return chains
