# PoC: semantic search for privacy policies

This project is based on the [Princeton-Leuven Privacy Policy dataset](https://privacypolicies.cs.princeton.edu/), a 
dataset of over a million privacy policies spanning 20+ years.

An efficient search engine would help practitioners and policymakers quickly answer questions about privacy policies
like: "What kind of information did Facebook collect in 2010?", "When did Google include GDPR compliance?"

This repo demonstrates **semantic search**, a step towards RAG (Retrieval Augment Generation) to support answering 
natural language questions from the privacy policy dataset.

#### Acknowledgements

The code and deployment setup is heavily inspired by [this article](https://aseifert.com/p/serverless-sentence-transformer/).

## Installation
The code can be installed with [poetry](https://python-poetry.org/docs/):

```bash
git clone git@github.com:privacy-policy-search/semantic-search-poc.git
cd semantic-search-poc
poetry install --all-extras
```

## Usage

For demonstration purposes, this repo uses HuggingFace's 
[SentenceTransformers](https://huggingface.co/sentence-transformers).

It also includes a small sample of the privacy policies. Request access to the 
[full dataset](https://privacypolicies.cs.princeton.edu/) to unlock the full functionality.

### Local

Run locally with:

```
poetry run python save_model.py
poetry run python handler.py
```

### Deployment

All configuration files are provided for deployment on AWS Lambda and ECR with the 
[serverless framework](https://www.serverless.com/framework/docs/getting-started).

**Create ECR Repo**

You must have an AWS account, the AWS CLI installed (e.g., `brew install awscli`), and be 
[authenticated](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-authentication.html).

```bash
aws ecr create-repository --repository-name privacypolicyfinder-repo
```

Make note of the repository URI for the following steps.

You can use the `justfile_example` provided to authenticate into the newly created ECR repository. Just fill in the 
missing fields, rename it to `justfile` and run:

```bash
just auth
```

**Deployment**

You must follow these steps at least once before running the `deploy` recipe:
1. Run `poetry run python save_model.py` if you haven't yet.
2. Build the docker image and then push it
```bash
docker build -t privacypolicyfinder . --platform=linux/x86_64
docker tag privacypolicyfinder <repoUri>
docker push <repoUri>
````
3. Make note of the digest for the next step.
3. Rename `serverless_example.yml` to `serverless.yml` and fill in image in this format: <repoUri>@<digest>
4. Run `serverless deploy`

**Query**

You can send in a new event following the AWS Lambda example format. You can use and edit the provided `event.json` 
and run:

```bash
just query
```