# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Idempotent fixtures for the isolated Compose database; never use a hosted database."""

from django.db import transaction
from django.utils import timezone
from plane.db.models import User, Profile, Workspace, WorkspaceMember, Project, ProjectMember, State, Issue
from plane.db.models.state import DEFAULT_STATES
from plane.license.models import Instance, InstanceAdmin

with transaction.atomic():
    instance, _ = Instance.objects.get_or_create(
        instance_id="niteshift-local",
        defaults=dict(
            instance_name="Niteshift",
            current_version="1.4.2",
            last_checked_at=timezone.now(),
            is_setup_done=True,
            is_signup_screen_visited=True,
            is_telemetry_enabled=False,
            is_support_required=False,
            is_test=True,
        ),
    )
    user, created = User.objects.get_or_create(
        email="developer@example.com",
        defaults=dict(
            username="niteshift-developer",
            first_name="Plane",
            last_name="Developer",
            display_name="Developer",
            is_email_verified=True,
        ),
    )
    if created:
        user.set_password("Niteshift-Local-Plane-2026!")
        user.save()
    InstanceAdmin.objects.get_or_create(instance=instance, user=user, defaults={"role": 20})
    workspace, _ = Workspace.objects.get_or_create(slug="niteshift", defaults={"name": "Niteshift", "owner": user})
    WorkspaceMember.objects.get_or_create(workspace=workspace, member=user, defaults={"role": 20})
    Profile.objects.get_or_create(
        user=user,
        defaults=dict(
            is_onboarded=True,
            is_tour_completed=True,
            is_navigation_tour_completed=True,
            last_workspace_id=workspace.id,
            onboarding_step={
                "profile_complete": True,
                "workspace_create": True,
                "workspace_invite": True,
                "workspace_join": True,
            },
        ),
    )
    project, _ = Project.objects.get_or_create(
        workspace=workspace, identifier="DEMO", defaults={"name": "Getting started", "created_by": user}
    )
    ProjectMember.objects.get_or_create(workspace=workspace, project=project, member=user, defaults={"role": 20})
    for definition in DEFAULT_STATES:
        if definition["group"] != "triage":
            State.objects.get_or_create(
                workspace=workspace, project=project, name=definition["name"], defaults=definition
            )
    state = State.objects.get(project=project, name="Todo")
    for name in ["Explore your workspace", "Create your first project", "Try the live editor"]:
        Issue.objects.get_or_create(
            workspace=workspace, project=project, name=name, defaults={"state": state, "created_by": user}
        )
print("Development workspace ready: niteshift / Getting started")
