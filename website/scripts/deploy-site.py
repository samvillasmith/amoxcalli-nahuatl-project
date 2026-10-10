#!/usr/bin/env python3
"""Publish the public website and add its Neon search origin without deleting assets.

Example (run from the linked Neon workspace):
  python website/scripts/deploy-site.py --site website \
    --function-url https://YOUR-FUNCTION-HOST --env .env.local --dry-run

Dry runs read AWS configuration, validate the deployment, and print safe metadata.
They never upload, update CloudFront, create policies, invalidate, or save backups.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
import mimetypes
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit
from uuid import uuid4


BUCKET = "fcn-nahuatl-website"
DISTRIBUTION = "E1XNT9YCJ5QMJJ"
ORIGIN_ID = "AmoxcalliLexiconAPI"
CACHE_POLICY_NAME = "AmoxcalliLexiconSearch-v1"
REQUEST_POLICY_NAME = "AmoxcalliLexiconQueryStrings-v1"
MANAGED_CACHE_POLICY_NAME = "Managed-CachingDisabled"
MANAGED_REQUEST_POLICY_NAME = "Managed-AllViewerExceptHostHeader"
QUERY_KEYS = ["q", "source", "offset", "limit", "pos"]
ROOT_DOCUMENTS = {
    "core_premises.md",
    "founding_charter_v0.1.md",
    "mission_statements.md",
    "msn_convergence_target.md",
    "register_charter_v0.1.md",
    "success_criteria.md",
}
STATIC_EXTENSIONS = {
    ".html", ".css", ".js", ".mjs", ".json", ".md", ".txt", ".xml",
    ".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".ico",
    ".woff", ".woff2", ".ttf", ".otf", ".pdf", ".mp3", ".mp4", ".webm",
}
EXCLUDED_COMPONENTS = {"sql", "scripts", "functions", "node_modules", "__pycache__"}
TEXT_TYPES = {
    ".html": "text/html", ".css": "text/css", ".js": "text/javascript",
    ".mjs": "text/javascript", ".json": "application/json",
    ".md": "text/markdown", ".txt": "text/plain", ".xml": "application/xml",
    ".svg": "image/svg+xml",
}


class DeploymentError(Exception):
    """A deployment error whose message is safe to show without credentials."""


def read_origin_secret(env_file: Path) -> str:
    if not env_file.is_file():
        raise DeploymentError("The supplied environment file does not exist.")
    secret = None
    for line in env_file.read_text(encoding="utf-8-sig").splitlines():
        match = re.match(r"^\s*(?:export\s+)?AMOXCALLI_ORIGIN_SECRET\s*=\s*(.*?)\s*$", line)
        if match:
            value = match.group(1)
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            secret = value
    if not secret or len(secret) < 32 or any(ord(char) < 32 or ord(char) > 126 for char in secret):
        raise DeploymentError("AMOXCALLI_ORIGIN_SECRET must be a nonempty printable secret of at least 32 characters.")
    return secret


def parse_function_url(value: str) -> tuple[str, str]:
    try:
        parsed = urlsplit(value)
        valid_port = parsed.port in (None, 443)
    except ValueError:
        raise DeploymentError("The function URL is invalid.") from None
    if (
        parsed.scheme != "https" or not parsed.hostname or not valid_port
        or parsed.username or parsed.password or parsed.query or parsed.fragment
        or not re.fullmatch(r"[a-zA-Z0-9.-]+", parsed.hostname)
    ):
        raise DeploymentError("Use the function's HTTPS base URL without credentials, query strings, or fragments.")
    return parsed.hostname, parsed.path.rstrip("/")


def public_files(site: Path) -> list[tuple[Path, str]]:
    if not site.is_dir() or not (site / "index.html").is_file():
        raise DeploymentError("The site directory must contain index.html.")
    selected = []
    for file in sorted(site.rglob("*")):
        if not file.is_file():
            continue
        relative = file.relative_to(site)
        parts = relative.parts
        if any(part.startswith(".") or part.lower() in EXCLUDED_COMPONENTS for part in parts):
            continue
        allowed = (
            relative.as_posix() == "index.html"
            or (len(parts) == 1 and file.name in ROOT_DOCUMENTS)
            or (len(parts) > 1 and parts[0] in {"assets", "msn"})
        )
        if not allowed or file.suffix.lower() not in STATIC_EXTENSIONS:
            continue
        if file.is_symlink() or not file.resolve().is_relative_to(site):
            raise DeploymentError("A public file resolves outside the site directory.")
        if file.suffix.lower() in TEXT_TYPES:
            # Refuse accidentally mislabeled files instead of publishing unreadable text.
            file.read_text(encoding="utf-8-sig")
        selected.append((file, relative.as_posix()))
    return selected


def content_metadata(file: Path) -> dict[str, str]:
    suffix = file.suffix.lower()
    content_type = TEXT_TYPES.get(suffix)
    if content_type:
        content_type += "; charset=utf-8"
    else:
        content_type = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
    return {
        "ContentType": content_type,
        "CacheControl": "no-cache, max-age=0, must-revalidate" if suffix == ".html" else "public, max-age=300",
    }


def cache_policy_config() -> dict:
    return {
        "Name": CACHE_POLICY_NAME,
        "Comment": "Public Nahuatl lexicon search, partitioned by search parameters",
        "MinTTL": 0,
        "DefaultTTL": 60,
        "MaxTTL": 300,
        "ParametersInCacheKeyAndForwardedToOrigin": {
            "EnableAcceptEncodingGzip": True,
            "EnableAcceptEncodingBrotli": True,
            "HeadersConfig": {"HeaderBehavior": "none"},
            "CookiesConfig": {"CookieBehavior": "none"},
            "QueryStringsConfig": {
                "QueryStringBehavior": "whitelist",
                "QueryStrings": {"Quantity": len(QUERY_KEYS), "Items": QUERY_KEYS},
            },
        },
    }


def request_policy_config() -> dict:
    return {
        "Name": REQUEST_POLICY_NAME,
        "Comment": "Forward query strings to public lexicon API without viewer cookies or headers",
        "HeadersConfig": {"HeaderBehavior": "none"},
        "CookiesConfig": {"CookieBehavior": "none"},
        "QueryStringsConfig": {"QueryStringBehavior": "all"},
    }


def comparable_policy(value):
    if isinstance(value, dict):
        return {key: comparable_policy(item) for key, item in value.items()}
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return sorted(value)
    return value


def find_policy(client, kind: str, desired: dict) -> str | None:
    operation = getattr(client, f"list_{kind}_policies")
    response_key = "CachePolicyList" if kind == "cache" else "OriginRequestPolicyList"
    policy_key = "CachePolicy" if kind == "cache" else "OriginRequestPolicy"
    config_key = f"{policy_key}Config"
    marker = None
    while True:
        response = operation(Type="custom", **({"Marker": marker} if marker else {}))
        collection = response.get(response_key, {})
        for item in collection.get("Items", []):
            policy = item[policy_key]
            config = policy[config_key]
            if config.get("Name") == desired["Name"]:
                # A named policy may be shared by other distributions; do not mutate it.
                current = {key: value for key, value in config.items() if key != "Comment"}
                expected = {key: value for key, value in desired.items() if key != "Comment"}
                if comparable_policy(current) != comparable_policy(expected):
                    raise DeploymentError(f"Existing policy {desired['Name']} differs from the required policy; review it before deployment.")
                return policy["Id"]
        marker = collection.get("NextMarker")
        if not marker:
            return None


def ensure_policy(client, kind: str, desired: dict, existing: str | None) -> str:
    if existing:
        return existing
    if kind == "cache":
        result = client.create_cache_policy(CachePolicyConfig=desired)
        return result["CachePolicy"]["Id"]
    result = client.create_origin_request_policy(OriginRequestPolicyConfig=desired)
    return result["OriginRequestPolicy"]["Id"]


def find_managed_policy(client, kind: str, name: str) -> str:
    operation = getattr(client, f"list_{kind}_policies")
    collection_key = "CachePolicyList" if kind == "cache" else "OriginRequestPolicyList"
    policy_key = "CachePolicy" if kind == "cache" else "OriginRequestPolicy"
    marker = None
    while True:
        response = operation(Type="managed", **({"Marker": marker} if marker else {}))
        collection = response.get(collection_key, {})
        for item in collection.get("Items", []):
            policy = item[policy_key]
            if policy[f"{policy_key}Config"].get("Name") == name:
                return policy["Id"]
        marker = collection.get("NextMarker")
        if not marker:
            raise DeploymentError(f"Required AWS managed policy {name} was not found.")


def distribution_with_api(previous: dict, domain: str, origin_path: str, secret: str,
                          cache_id: str, request_id: str) -> dict:
    updated = deepcopy(previous)
    origins = updated["Origins"].setdefault("Items", [])
    matching = [index for index, origin in enumerate(origins) if origin["Id"] == ORIGIN_ID]
    if len(matching) > 1:
        raise DeploymentError("The distribution has duplicate lexicon origin IDs.")
    origin = deepcopy(origins[matching[0]]) if matching else {}
    origin.update({"Id": ORIGIN_ID, "DomainName": domain, "OriginPath": origin_path})
    for incompatible in ("S3OriginConfig", "VpcOriginConfig", "OriginAccessControlId"):
        origin.pop(incompatible, None)
    headers = [header for header in origin.get("CustomHeaders", {}).get("Items", [])
               if header["HeaderName"].lower() != "x-secret"]
    headers.append({"HeaderName": "X-Secret", "HeaderValue": secret})
    origin["CustomHeaders"] = {"Quantity": len(headers), "Items": headers}
    origin.setdefault("CustomOriginConfig", {}).update({
        "HTTPPort": 80, "HTTPSPort": 443, "OriginProtocolPolicy": "https-only",
        "OriginSslProtocols": {"Quantity": 1, "Items": ["TLSv1.2"]},
        "OriginReadTimeout": 30, "OriginKeepaliveTimeout": 5,
    })
    origin.setdefault("ConnectionAttempts", 3)
    origin.setdefault("ConnectionTimeout", 10)
    if matching:
        origins[matching[0]] = origin
    else:
        origins.append(origin)
    updated["Origins"]["Quantity"] = len(origins)

    collection = updated.setdefault("CacheBehaviors", {"Quantity": 0})
    behaviors = collection.setdefault("Items", [])
    matching = [index for index, behavior in enumerate(behaviors)
                if behavior["PathPattern"].lstrip("/") == "api/*"]
    if len(matching) > 1:
        raise DeploymentError("The distribution has duplicate api/* cache behaviors.")
    behavior = deepcopy(behaviors[matching[0]]) if matching else {
        "TrustedSigners": {"Enabled": False, "Quantity": 0},
        "TrustedKeyGroups": {"Enabled": False, "Quantity": 0},
        "LambdaFunctionAssociations": {"Quantity": 0},
        "FunctionAssociations": {"Quantity": 0},
        "FieldLevelEncryptionId": "",
        "SmoothStreaming": False,
    }
    behavior.update({
        "PathPattern": "api/*", "TargetOriginId": ORIGIN_ID,
        "ViewerProtocolPolicy": "redirect-to-https", "Compress": True,
        "AllowedMethods": {
            "Quantity": 3, "Items": ["GET", "HEAD", "OPTIONS"],
            "CachedMethods": {"Quantity": 3, "Items": ["GET", "HEAD", "OPTIONS"]},
        },
        "CachePolicyId": cache_id, "OriginRequestPolicyId": request_id,
    })
    for legacy in ("ForwardedValues", "MinTTL", "DefaultTTL", "MaxTTL"):
        behavior.pop(legacy, None)
    if matching:
        behaviors[matching[0]] = behavior
    else:
        # Keep every prior behavior in its relative order; prevent a wildcard from hiding the API.
        behaviors.insert(0, behavior)
    collection["Quantity"] = len(behaviors)
    return updated


def save_distribution_backup(env_file: Path, etag: str, config: dict) -> Path:
    directory = env_file.parent / ".deployment-state"
    directory.mkdir(exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    path = directory / f"cloudfront-{DISTRIBUTION}-{timestamp}.json"
    # This may contain an existing origin secret. Keep .deployment-state/ gitignored.
    with path.open("x", encoding="utf-8") as output:
        json.dump({"distributionId": DISTRIBUTION, "ETag": etag, "DistributionConfig": config}, output, indent=2)
        output.write("\n")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--function-url", required=True)
    parser.add_argument("--env", type=Path, required=True, help="Gitignored environment file holding AMOXCALLI_ORIGIN_SECRET")
    parser.add_argument("--dry-run", action="store_true", help="Validate and inspect only; make no local or remote changes")
    args = parser.parse_args()

    site = args.site.resolve()
    env_file = args.env.resolve()
    secret = read_origin_secret(env_file)
    domain, origin_path = parse_function_url(args.function_url)
    files = public_files(site)

    # Some bundled Windows runtimes have incompatible pyOpenSSL. urllib3's standard
    # library TLS implementation remains enabled, including certificate verification.
    sys.modules["OpenSSL"] = None
    import boto3
    from botocore.validate import validate_parameters

    session = boto3.Session()
    cloudfront = session.client("cloudfront")
    s3 = session.client("s3")
    s3.head_bucket(Bucket=BUCKET)
    live = cloudfront.get_distribution_config(Id=DISTRIBUTION)
    previous = live["DistributionConfig"]
    if not any(BUCKET in origin["DomainName"] for origin in previous["Origins"].get("Items", [])):
        raise DeploymentError("The existing distribution does not reference the expected website bucket.")
    # Managed policies work on the existing Free pricing plan. Never upgrade the
    # account or attach unsupported custom policies to this distribution.
    cache_id = find_managed_policy(cloudfront, "cache", MANAGED_CACHE_POLICY_NAME)
    request_id = find_managed_policy(cloudfront, "origin_request", MANAGED_REQUEST_POLICY_NAME)
    proposed = distribution_with_api(previous, domain, origin_path, secret,
                                     cache_id, request_id)
    operation = cloudfront.meta.service_model.operation_model("UpdateDistribution")
    validate_parameters({"Id": DISTRIBUTION, "IfMatch": live["ETag"], "DistributionConfig": proposed}, operation.input_shape)
    summary = {
        "mode": "dry-run" if args.dry_run else "deploy",
        "bucket": BUCKET, "distribution": DISTRIBUTION,
        "publicFiles": [key for _, key in files],
        "apiOrigin": f"https://{domain}{origin_path}",
        "apiPath": "api/*", "queryStrings": "all forwarded; edge API caching disabled",
        "cachePolicy": MANAGED_CACHE_POLICY_NAME,
        "originRequestPolicy": MANAGED_REQUEST_POLICY_NAME,
        "distributionChange": previous != proposed,
    }
    print(json.dumps(summary, indent=2))
    if args.dry_run:
        print("Validated. No local or remote changes were made.")
        return 0

    updated = distribution_with_api(previous, domain, origin_path, secret, cache_id, request_id)
    if previous != updated:
        backup = save_distribution_backup(env_file, live["ETag"], previous)
        print(f"Saved previous distribution configuration: {backup.name}")
        result = cloudfront.update_distribution(Id=DISTRIBUTION, IfMatch=live["ETag"], DistributionConfig=updated)
        print(f"CloudFront configuration: {result['Distribution']['Status']}")
    else:
        print("CloudFront configuration already matches; no distribution update needed.")
    for file, key in files:
        s3.upload_file(str(file), BUCKET, key, ExtraArgs=content_metadata(file))
        print(f"Published: {key}")
    invalidation = cloudfront.create_invalidation(
        DistributionId=DISTRIBUTION,
        InvalidationBatch={"Paths": {"Quantity": 1, "Items": ["/*"]},
                           "CallerReference": f"amoxcalli-site-{uuid4()}"},
    )["Invalidation"]
    print(f"Invalidation {invalidation['Id']}: {invalidation['Status']}")
    print("Website: https://amoxcalli.org/")
    print("Search API: https://amoxcalli.org/api/search")
    print("Deployment submitted. Verify the public site after CloudFront propagation completes.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except DeploymentError as error:
        print(f"Deployment stopped: {error}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Deployment interrupted.", file=sys.stderr)
        sys.exit(130)
    except Exception as error:
        # AWS/network exceptions can include request headers or credentials in their
        # messages. Only expose the operation and a bounded service error code.
        response = getattr(error, "response", {})
        code = response.get("Error", {}).get("Code", type(error).__name__)
        safe_code = re.sub(r"[^A-Za-z0-9_.-]", "", str(code))[:80]
        operation = re.sub(r"[^A-Za-z0-9_.-]", "", str(getattr(error, "operation_name", "validation or network request")))[:80]
        print(f"Deployment stopped during {operation}: {safe_code}. No credentials are shown.", file=sys.stderr)
        service_message = response.get("Error", {}).get("Message", "")
        if service_message:
            if "--env" in sys.argv:
                try:
                    credential = read_origin_secret(Path(sys.argv[sys.argv.index("--env") + 1]))
                    service_message = service_message.replace(credential, "[private credential]")
                except (ValueError, IndexError, DeploymentError):
                    service_message = "Service rejected the configuration."
            service_message = re.sub(r"postgres(?:ql)?://\S+", "[database connection]", service_message)
            print(service_message[:600], file=sys.stderr)
        sys.exit(1)
