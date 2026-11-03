# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Development settings behind the Niteshift HTTPS preview proxy."""

from plane.settings.local import *  # noqa: F403

# Match production's forwarded-scheme handling so S3 links use the viewer's scheme.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_TRUSTED_ORIGINS = [*CSRF_TRUSTED_ORIGINS, "https://*.preview.niteshift.dev"]  # noqa: F405
