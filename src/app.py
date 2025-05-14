"""app module."""

import base64
from typing import Literal, Optional

from fastapi import FastAPI
import grpc
from pydantic import BaseModel, Base64Bytes

from utils import (
    chunk_text,
    build_translate_pipeline,
)

from attestation_container_pb2_grpc import AttestationContainerStub
import attestation_container_pb2

app = FastAPI()


class TranslateItemReq(BaseModel):
    """Item request for /translate endpoint."""

    doc: str
    src_lang: Literal["en", "fr"]
    dst_lang: Literal["en", "fr"]
    hf_token: Optional[str]


class TranslateItemResp(BaseModel):
    """Item response for /translate endpoint."""

    result: str


class AttestationReportItemReq(BaseModel):
    """Item request for /report endpoint."""

    report_data: Optional[Base64Bytes]


class AttestationReportItemResp(BaseModel):
    """Item response for /report endpoint."""

    attestation: Base64Bytes
    platform_certificates: str
    uvm_endorsements: Base64Bytes


@app.get("/")
async def root():
    """Root for health check."""
    return "Hello World!"


@app.post("/report")
async def attestation_report(item: AttestationReportItemReq):
    """Attestation report for AMD SEV-SNP."""
    channel = grpc.insecure_channel(
        "unix:///mnt/uds/attestation-container.sock",
        options=(("grpc.default_authority", "localhost"),),
    )
    stub = AttestationContainerStub(channel)
    request = attestation_container_pb2.FetchAttestationRequest(
        report_data=item.report_data if item.report_data else b"\x00" * 64
    )

    response = stub.FetchAttestation(request)

    return AttestationReportItemResp(
        attestation=base64.b64encode(response.attestation),
        platform_certificates=response.platform_certificates.decode("utf-8"),
        uvm_endorsements=base64.b64encode(response.uvm_endorsements),
    )


@app.post("/translate")
async def translate(item: TranslateItemReq):
    """Translate text."""
    if item.src_lang == item.dst_lang:
        return ("Error: ", 400)

    model_name = f"Helsinki-NLP/opus-mt-{item.src_lang}-{item.dst_lang}"

    try:
        translate_pipeline = build_translate_pipeline(model_name, item.hf_token)
        all_replies = []
        chunks = chunk_text(item.doc, model_name, 200)
        for chunk in chunks:
            data = {"translater": {"prompt": f"{chunk}"}}
            result = translate_pipeline.run(data=data)["translater"]["replies"][0]
            all_replies.append(result)
        combined_result = " ".join(all_replies)
    except OSError:
        return ("Error: model does not support these languages for translation.", 400)
    except ValueError as e:
        return (f"Error: {e}", 400)

    return TranslateItemResp(result=combined_result)
