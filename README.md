# Demo AI for Azure Confidential Containers on AKS

## Overview

Python demo using [haystack](https://haystack.deepset.ai) to translate french to english and english to french through an HTTP service.
An additional endpoint `/report` allows to fetch the AMD SEV-SNP attestation report of the running pod by using Microsoft sidecar's [attestation container](https://github.com/microsoft/confidential-sidecar-containers/tree/v2.10/cmd/attestation-container).
It can be then be verified with [sev-verifier](https://github.com/Cosmian/sev-verifier).

## Deployment

First use [azure-cli](https://github.com/Azure/azure-cli) to generate kata policy

```bash
az confcom katapolicygen -y cc-ai-demo.yaml
```

then

```bash
kubectl apply -f cc-ai-demo.yaml
```

check status with

```bash
kubectl describe pod cc-ai-demo
# or
kubectl get pods
```

and finally, save the external IP address to `$IP_ADDR`

```bash
export IP_ADDR="$(kubectl get service cc-ai-demo-service --output jsonpath='{.status.loadBalancer.ingress[0].ip}')"
```

## Usage

If `Helsinki-NLP/opus-mt-fr-en` or `Helsinki-NLP/opus-mt-fr-en` models are not in `/mnt/azuredisk/data/` folder, it will try to download from [huggingface](https://huggingface.co/) and `hf_token` is mandatory.

```bash
# provide `hf_token` if models are not available offline
curl -X POST --data '{"doc": "Hello World!", "src_lang": "en", "dst_lang": "fr", "hf_token": "null"}' --header "Content-Type: application/json" http://$IP_ADDR:5555/translate
```

## Remote attestation

```bash
# generate 64 random bytes base64-encoded
export REPORT_DATA=$(openssl rand 64 | openssl base64 -A)
curl -X POST --header "Content-Type: application/json" --data "{\"report_data\": \"$REPORT_DATA\"}" http://$IP_ADDR:5555/report > report.json
sev-verify --json-file report.json --b64-report-data "$REPORT_DATA"
```