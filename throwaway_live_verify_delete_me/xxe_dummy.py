"""Throwaway fixture file — not real code, see ../README.md."""

from xml.etree import ElementTree as ET


def dummy_parse_uploaded_xml(raw_xml: str):
    """`ElementTree.fromstring` with no external-entity hardening — XXE
    shape, intentional in this disposable fixture."""
    return ET.fromstring(raw_xml)  # noqa: S314
