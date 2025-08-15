"""TypedDict definitions for Mintlify docs.json configuration structure."""

from __future__ import annotations

from typing import TypedDict


class MintlifyConfig(TypedDict):
    """Mintlify config."""

    navigation: Navigation


class Navigation(TypedDict, total=False):
    """Navigation configuration."""

    versions: list[NavigationVersion] | None


class NavigationVersion(TypedDict, total=False):
    """Version within a navigation."""

    version: str
    dropdowns: list[NavigationDropdown] | None
    tabs: list[NavigationTab] | None


class NavigationDropdown(TypedDict, total=False):
    """Dropdown within a version."""

    dropdown: str
    icon: str
    tabs: list[NavigationTab] | None


class NavigationTab(TypedDict, total=False):
    """Tab within a version."""

    tab: str
    groups: list[NavigationGroup] | None


class NavigationGroup(TypedDict):
    """Group within a tab."""

    group: str
    pages: list[str | NavigationGroup]
