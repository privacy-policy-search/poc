try:
    import unzip_requirements
except ImportError:
    pass

import os
import json
import traceback
import logging
from dataclasses import asdict
from functools import lru_cache
from sentence_transformers import SentenceTransformer
from privacypolicyfinder import PrivacyPolicy, find_privacy_policy, get_vectors


RAW_PRIVACY_POLICIES = "data"

logger = logging.getLogger("test")
logger.setLevel(logging.INFO)


@lru_cache
def get_model(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name)


def split_filename(filename):
    filename_no_extension, _ = filename.split(".")
    return filename_no_extension.split("_")


@lru_cache
def get_privacy_policies() -> list[PrivacyPolicy]:
    dir_name = RAW_PRIVACY_POLICIES
    filenames = ["linux_2019.txt", "usenix_2016.txt"]

    privacy_policies = []
    for f in filenames:
        domain, year = split_filename(f)

        with open(os.path.join(dir_name, f)) as fp:
            text = fp.readlines()
        policy = PrivacyPolicy(domain, year, text)
        privacy_policies.append(policy)

    return privacy_policies


def lambda_handler(event, context):
    logger.info(event)

    try:
        request = json.loads(event["body"])
        query = json.loads(request["body"]).get("query")
        assert query, f"`query` is required"
        n = int(request.get("n", 32))

        model = get_model("model/")
        privacy_policies = get_privacy_policies()
        embeddings = get_vectors(model, privacy_policies)

        response = {
            "privacy_policies": [
                asdict(e)
                for e in find_privacy_policy(
                    query=query, privacy_policies=privacy_policies, model=model, embeddings=embeddings, n=n
                )
            ]
        }

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
            "body": json.dumps(response),
        }
    except Exception as e:
        logger.error(repr(e))

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            },
            "body": json.dumps({"error": str(traceback.format_exc()), "event": event, "context": str(context)}),
        }


if __name__ == "__main__":
    print(lambda_handler({"body": json.dumps({"query": "usenix"})}, None)["body"])