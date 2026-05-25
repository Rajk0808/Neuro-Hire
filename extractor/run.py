"""
CLI / Example Runner
====================
    python run.py --mode hybrid --input resumes/
    python run.py --mode fast   --text "John Smith..."
    python run.py --mode llm    --file resume.txt
"""

import argparse
import json
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

from orchestrator import ResumeOrchestrator, ExtractionMode


# ── Demo resume (used when no input is provided) ──────────────

DEMO_RESUME = """
Maheshwar Kuchana 

London • 

maheshwar.kuchana@gmail.com • linkedin.com/in/maheshwarkuchana 

Senior Machine Learning Engineer 

Senior Machine Learning Engineer with 5+ years of experience in designing, developing, and deploying production-grade AI & GenAI systems at scale. Expertise in leveraging AI frameworks, cloud technologies (Azure, AWS), and MLOps practices for robust product lifecycle management. Proven track record of building end-to-end AI products, optimizing business decisions, and automating processes through cutting-edge AI techniques across the retail, healthcare, �nance, insurance and banking sectors. Adept at working in cross-functional teams to deliver high-impact AI solutions that drive signi�cant business value. 

SKILLS 

Gen AI: Large  Language  Models  ( LLM) , LangChain, LangGraph, AgentOps, Multi- Agentic  Systems, MCP 

Software Engineering: Kubernetes, Terraform, Docker, Amazon  Web  Services, Microsoft  Azure, Azure  Data  Factory, Azure Pipelines, Databricks, Delta  Lake, MLFlow, MLOps, Python, PySpark, GitHub  Actions, GitLab  Pipelines, FastAPI, Flask, Data Engineering, Event- Driven  Architecture, Software  Architecture, Design  Patterns, Testing, Power  BI, SQL, NoSQL  DB, Vector  DB 

ML & Data Science: PyTorch, TensorFlow, Computer  Vision, CNN, Self- Supervised  Learning, Medical  Imaging, MONAI, Feature Engineering, Statistical  analysis, Hypothesis  testing, A/ B  testing, Autoencoders, Feature  Store 

WORK EXPERIENCE 

Faculty.ai • London 

Dec 2024 - Present 

Senior Machine Learning Engineer 

• Architected a production‐grade multi‐agent LangGraph platform on Azure Kubernetes Service (AKS) that automates KYC work�ows for an international investment bank, cutting manual review time by 70%

• Designed AgentOps toolkit (guardrails, tracing, of�ine evals, CI/CD via GitLab) enabling weekly releases with one‐click rollback and zero‐downtime migrations

• Implemented an event-driven based custom Agent-to-Agent (A2A) protocol with fault-tolerant orchestration (horizontal autoscaling, circuit-breakers) that coordinates 100+ concurrent agents, sustaining peak load and cutting cloud spend 25%

• Led development of a multi‐agent group‐life claims‐automation system leveraging Azure Document Intelligence and GPT‐powered agents to process 1 000+ claims/day with 99.9% SLA compliance

• Conducted enterprise AI maturity assessments and advised senior leadership on roadmap, driving adoption of secure MLOps best practices across three business units

ASOS.com • London 

Sep 2022 - Nov 2024 

Machine Learning Engineer 

• Built and operated a cloud‐native ML & data platform on Azure Databricks, Delta Lake and ML�ow, provisioned via Terraform. Automated notebook work�ows, feature pipelines and model‐registry promotion, cutting research to production lead time 40% while serving 200 K+ predictions per month for promotion and clearance decisions

• Delivered Promotions AI project that automates SKU selection across all customer touchpoints, scaling promotion work�ows to multiple merchandising use cases. Tight integration with Azure Databricks and the merchandising API enabled data‐driven decisions that generated £7.5 M incremental revenue in FY‐23 and £2.3 M in FY‐24 Q1

• Built MLOps for Clearance AI, markdown‐price optimiser, computing bi‐monthly across multiple regions. regional markdowns by fusing demand‐elasticity models with stock‐age heuristics; streamed dynamic price feeds to merchandising APIs, boosting sell‐through 3.6%.

• Automated ingestion, validation and enrichment for datasets with Delta Lake and PySpark; co‐authored reusable transformation and connector libraries that cut new‐source onboarding time 60% and materially reduced data‐pipeline incidents, giving analysts reliable, timely datasets

• Standardised MLOps across Promotions AI, Clearance AI and ingestion pipelines: Dockerised inference, uni�ed ML�ow lineage, blue‐green releases via Azure Pipelines, and an automated A/B test harness that cut experiment turnaround 50%, sustained 99.9% SLA and halved incident MTTR

• Built cookiecutter‐based project templates and Databricks job scaffolds, along with playbooks for distributed training on Spark clusters; enabled data scientists to launch new ML experiments in under an hour, standardising best practices and accelerating iteration cycles

• Created interactive Power BI and Azure‐native dashboards that surface KPI impact, data lineage and model health to merchandising, �nance and engineering teams. Authored technical runbooks and reproducible notebooks to accelerate onboarding and ensure regulatory audit readiness

Scienaptic Systems • India 

Oct 2020 - Jan 2021 

Machine Learning Engineer • Full-Time 

• Developed an AI‐driven document‐processing pipeline that automates credit underwriting; delivered �rst production version in 2 months and adopted by 3 Tier‐1 banks, cutting manual review time 35%

• Implemented PDF extraction (PDFMiner, PyPDF2) and Amazon Textract OCR, exposing risk‐scoring models via containerised REST microservices on AWS (EC2, S3, SQS, SNS) with auto‐scaling and comprehensive observability

• Instituted enterprise‐grade MLOps—model versioning, reproducibility, audit trails—forming a reusable framework leveraged by 6 product teams across the company

Adventum Advanced Solutions • India 

May 2019 - Sep 2020 

Arti�cial Intelligence Engineer • Full-Time 

• Developed the full lifecycle of an AI diagnostics platform for diabetic retinopathy and glaucoma participating in patient‐data acquisition, image annotation work�ows, preprocessing pipelines and cloud deployment gaining hands‐on exposure to every stage of regulated medical‐AI development in startup environment.

• Curated and quality‐controlled ~25 k OCT volumes and fundus photographs stored as DICOM from multi‐vendor PACS; scripted ITK‐Snap / 3D Slicer automations that lifted annotation throughput 40% and produced a clean training corpus for downstream models

• Designed, trained and iteratively re�ned custom U‐Net and ResNet variants for retinal‐�uid segmentation, layer delineation and anomaly classi�cation; achieved 93% sensitivity at 95% speci�city during blinded clinical validation, meeting internal go‐to‐market thresholds

• Ran >400 experiment rounds on Databricks and on‐prem GPUs using PyTorch and MONAI, applying transfer learning and ensemble techniques; tracked all runs in ML�ow, which enabled reproducible ablation studies and rapid hyper‐parameter sweeps

• Packaged inference logic as Dockerised Flask microservices on AWS ECS, instrumented with CloudWatch and Prometheus exporters; an automated deployment work�ow cut rollout time from weekly to daily and supported clinician‐facing web apps

• Authored real‐time monitoring dashboards and slice‐level drift alerts that surfaced precision/recall by pathology and scanner type, reducing issue diagnosis time 40% and supporting post‐market surveillance obligations

• Collaborated closely with ophthalmologists, biomedical engineers and full‐stack developers—presenting model insights at weekly review boards and co‐ordinating small‐scale clinical trials

EDUCATION 

King's College London 

Master of Research in Healthcare Technologies in Arti�cial Intelligence • GPA: Distinction 

Sep 2021 - Sep 2022 

• Quantitative Imaging of the Shared Placenta in Twin Pregnancies – built a 3D vessel‐segmentation and super‐resolution pipeline in MONAI/PyTorch for Twin‐to‐Twin Transfusion Syndrome surgery planning; reduced manual annotation 60%. 

• Self‐Supervised Pre‐training for Retinal OCT Fluid Segmentation – cut labelled‐data requirements 70% while maintaining <2 µm mean surface error via contrastive pre‐training 

PUBLICATIONS 

Machine learning predicts live-birth occurrence before in-vitro fertilization treatment 

Dec 2020 

Nature Scienti�c Reports 

AI aiding in diagnosing, tracking recovery of COVID-19 using deep learning on Chest CT scans Nov 2020 Springer Multimedia Tools And Application 

International Journal For Research In Applied Science And Engineering Technology 

Fingerprint Matching-An Experimental Approach Jun 2020 
""".strip()


def main():
    parser = argparse.ArgumentParser(description="Resume NLP Extraction Pipeline")
    parser.add_argument("--mode",  choices=["fast", "hybrid", "llm"], default="hybrid")
    parser.add_argument("--input", help="Directory of .txt resume files")
    parser.add_argument("--file",  help="Single resume .txt file")
    parser.add_argument("--text",  help="Raw resume text string")
    parser.add_argument("--output",help="Output JSON file (default: stdout)")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    mode = ExtractionMode(args.mode)
    orch = ResumeOrchestrator(mode=mode, max_workers=args.workers)
    paths = []
    # ── Collect texts ─────────────────────────
    if args.input and Path(args.input).glob("*.pdf"):
        pdf_paths = list(Path(args.input).glob("*.pdf"))
        for pdf_path in pdf_paths:
            text = orch.pdf_to_text(pdf_path)
            if text:
                paths.append(pdf_path.with_suffix(".txt"))
                paths[-1].write_text(text, encoding="utf-8")
            else:
                logging.warning(f"Failed to extract text from {pdf_path}, skipping.")
        
        if args.input and Path(args.input).glob("*.docx"):
            doc_paths = list(Path(args.input).glob("*.docx"))
            for docx_path in doc_paths:
                text = orch.docx_to_text(docx_path)
                if text:
                    paths.append(docx_path.with_suffix(".txt"))
                    paths[-1].write_text(text, encoding="utf-8")
                else:
                    logging.warning(f"Failed to extract text from {docx_path}, skipping.")


        if not paths:
            sys.exit(f"No .txt files found in {args.input}")
        texts = [p.read_text(encoding="utf-8") for p in paths]
        print(f"Processing {len(texts)} resumes in {args.mode.upper()} mode…")
        results = orch.batch_extract(texts)
        output  = [r.to_dict() for r in results]

    elif args.file:
        text   = Path(args.file).read_text(encoding="utf-8")
        result = orch.extract(text)
        output = result.to_dict()

    elif args.text:
        result = orch.extract(args.text)
        output = result.to_dict()

    else:
        print("No input provided — running on demo resume.\n")
        result = orch.extract(DEMO_RESUME)
        output = result.to_dict()

    # ── Output ────────────────────────────────
    out_json = json.dumps(output, indent=2)
    if args.output:
        Path(args.output).write_text(out_json)
        print(f"Saved to {args.output}")
    else:
        print(out_json)


if __name__ == "__main__":

    import time 
    start_time = time.monotonic()
    main()
    end_time = time.monotonic()
    elapsed = end_time - start_time
    print(f"\nExecution time: {elapsed:.2f} seconds")



# nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free => 23.52 seconds 
