"""
Secure, cloud-friendly configuration.

Secrets are loaded from environment variables or Streamlit secrets:
- OPENAI_API_KEY
- GOOGLE_API_KEY
- GOOGLE_CX

Non-secret product/company data remains as plain constants.
"""

import os
import streamlit as st


def get_api_key(key_name: str):
    """Fetch API keys from env first, then from Streamlit secrets."""
    env_val = os.getenv(key_name)
    if env_val:
        return env_val
    try:
        if key_name == "OPENAI_API_KEY":
            return st.secrets["openai"]["api_key"]
        if key_name == "GOOGLE_API_KEY":
            return st.secrets["google"]["api_key"]
        if key_name == "GOOGLE_CX":
            return st.secrets["google"]["cx"]
    except Exception:
        pass
    return None


# Secrets (loaded at runtime)
openai_api_key = get_api_key("OPENAI_API_KEY")
google_api_key = get_api_key("GOOGLE_API_KEY")
google_cx = get_api_key("GOOGLE_CX")


# Product/company info (non-secret)
company_name = "Fr0ntierX"

core_tech = [
    "POLARIS, our secure multi-dimensional confidential computing solution that wraps any cloud workload within hardware-native confidential environments called TEEs. Runs on NVIDIA, AMD, and Intel hardware chips",
    "Secure key attestation, which consistently verifies whether cryptographic software and hardware keys are properly secured and compatible with the hardware demands of Polaris",
    "Protects data in use, in transit, and at rest",
    "Isolates workloads except for specifically authorized items; e.g. it maintains encryption even in the event of a breach, since it requires robust authentication to access anything other than information specifically authorized for any given user",
    "Can co-exist with any other security stack; easily deployable in a matter of minutes, unlike most confidential computing solutions",
    "TEEs; workloads are always executed within a confidential VM or GPU and managed keys",
    "Different varieties: Pro, AI, LLM, K8s",
    "Regular - stateless workload processing, good for data processing, transformation, cleaning etc",
    "Pro - secure processing and storage in cloud, disk, or database - e.g. stateful",
    "AI - Protects AI models/machine learning within TEE",
    "LLM - Secures documents and RAG with all features of AI",
    "K8s - Runs confidential node that protects Kubernetes, an orchestration tool, and Docker nodes as well",
    "Securely protects sensitive data",
    "Scalable, secure, peace-of-mind AI product",
]

value_props = [
    "Data is secure even in the event of a breach",
    "Leverages confidential computing on Intel, Nvidia, AMC, SRC, etc",
    "Compliance including SOC 2 Type 1, Type 2, ISO 27001, NIST; working on HIPAA",
    "Available with hardware-native keys on Azure and GCP",
    "Proprietary key management",
    "Polaris is open-source, free to use, and trusted by a variety of verticals",
]

positioning = [
    "We want to be Home Depot: DIY-friendly, but fully supported if necessary",
    "We are unlocking confidential computing capabalities that were invented in 2015-2017 by cloud hardware providers, but have not yet been capitalized on in an efficient software manner by anybody",
    "Basically, we're the iPhone — intuitive and inevitable. You won't know you needed it until you have it.",
    "Great for orgs moving to the cloud or transitioning to AI",
    "TAM in confidential computing: $5B today (mostly hardware) → $184B by 2032, $73B in software",
    "Cryptography-based",
    "Company got its start working on confidential blockchain wallets and eventually moved to just selling the security itself",
    "Member of Confidential Computing Consortium",
    "Easy to install: very few code changes, no kernel modifications, nothing. We're a wrapper that sits on top of your code: deep in your stack, sure, but not requiring any changes to it",
    "Collaborators: MITRE, NYU Stern (0.00005 acceptance), NVIDIA",
    "Working on Nvidia Hopper GPU",
    "Facilitates complex tech adoption",
    "Open-source: you trust yourself, not us or the cloud, and our code is there on Github if you're curious about it",
    "Free to use; $10k support tier",
    "Deep in tech stack, but not in the kernel (unlike competitors)",
    "Blockchain expertise (wallets, etc.)",
    "Only 4 known competitors globally",
    "Registered government contractor",
    "Red Hat model: accessible, open-source, and easy",
    "Customers: WB, NCAA, ImmutableX, LG, Carnival (PII), NM health exchange",
    "Team: Jonathan (ex-tech i-banker, cloud systems background)",
    "Team: Andrew (CEO/CSO, finance + applied math)",
    "Team: Jens (CTO, military intel & security, with our roots in blockchain)",
    "Team: Vlad (VP Eng., PhD AI + BMW)",
    "Team: Ensermu (blockchain dev)",
]
