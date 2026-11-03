# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

"""Sign in through existing Plane endpoints and export Playwright cookie state."""

import http.cookiejar
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Keep login cookies without following a redirect into a cold Vite server."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


base = "http://localhost:8888"
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar), NoRedirect())
for attempt in range(60):
    try:
        with opener.open(base + "/auth/get-csrf-token/", timeout=5) as response:
            json.load(response)["csrf_token"]
        break
    except (OSError, KeyError):
        if attempt == 59:
            raise
        time.sleep(2)

for endpoint, identity in [
    ("/auth/sign-in/", "/api/users/me/"),
    ("/api/instances/admins/sign-in/", "/api/instances/admins/me/"),
]:
    with opener.open(base + "/auth/get-csrf-token/", timeout=15) as response:
        csrf = json.load(response)["csrf_token"]
    data = urllib.parse.urlencode(
        {
            "email": "developer@example.com",
            "password": "Niteshift-Local-Plane-2026!",
            "csrfmiddlewaretoken": csrf,
        }
    ).encode()
    request = urllib.request.Request(base + endpoint, data=data, headers={"Referer": base + "/"})
    try:
        opener.open(request, timeout=15)
    except urllib.error.HTTPError as error:
        if error.code != 302:
            raise
    with opener.open(base + identity, timeout=15) as response:
        assert json.load(response)["email"] == "developer@example.com", "Development sign-in failed"

cookies = [
    {
        "name": c.name,
        "value": c.value,
        "domain": "localhost",
        "path": c.path,
        "expires": c.expires or -1,
        "httpOnly": c.has_nonstandard_attr("HttpOnly"),
        "secure": c.secure,
        "sameSite": "Lax",
    }
    for c in jar
]
Path(os.environ["NITESHIFT_AUTH_STATE_FILE"]).write_text(json.dumps({"cookies": cookies, "origins": []}))
print("Development web and admin preview sessions ready")
