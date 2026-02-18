# Gene Marker Explorer

## Overview

GeneMarker Explorer is a command line bioinformatics tool that integrates the Ensembl REST API and the Human Protein Atlas to retrieve structured gene metadata and tissue level RNA expression data.

Given a human gene symbol, the tool returns:

- Ensembl gene ID  
- Gene description  
- Chromosomal location  
- Strand orientation  
- Baseline Tissue level RNA expression values  

This project demonstrates API integration, clean architecture, and automated testing combined to build a reliable and structured bioinformatics application..

## Purpose

Gene related information is distributed across multiple biological databases. This application provides a simple, reproducible workflow that combines genomic metadata (Ensembl) with expression data (HPA) in a single query.

The project developed demonstrates:

- Object oriented design
- Abstract base classes 
- Factory pattern implementation
- Service layer separation
- Command line interface development
- Unit testing with pytest

## Installation

Requirements:

- Python 3.11.5
- requests == 2.31.0
- click == 8.0.4
- pytest == 7.4.0 (for testing)

Install dependencies:

pip install -r requirements.txt

## Usage

Run from the project root: 

python cli.py <GENE_SYMBOL>

Example: 

python cli.py EGFR

Output:

GeneMarker Explorer

 Looking up gene: EGFR

 Ensembl Gene Information:
   Ensembl ID:  ENSG00000146648
   Symbol: EGFR
   Description:     epidermal growth factor receptor [Source:HGNC Symbol;Acc:HGNC:3236]
   Sequence Region Name:    chr7
   Strand Information:    1

 Fetching tissue expression data...

 HPA Gene Information:
   Gene:  EGFR
   Ensembl ID: ENSG00000146648
   Description:     Epidermal growth factor receptor
   Tissue Expression:    [TissueExpression(tissue='placenta', ntpm=61.8)]

  Done!



The application:

- Resolves the gene symbol via Ensembl  
- Retrieves full gene metadata  
- Uses the Ensembl ID to query HPA  
- Displays  genomic and expression information  

## Project Structure 

gene_marker_explorer/


    connectors/
        __init__.py
        base.py
        ensembl.py
        factory.py
        hpa.py

    scripts/
        __init__.py
        script.py

    services/
        __init__.py
        gene_service.py

    tests/
        __init__.py
        tests.py

    .gitignore
     __init__.py
    cli.py 
    README.md
    requirements.txt

## Scope and Extensibility

The application integrates the Ensembl REST API and the Human Protein Atlas to retrieve genomic metadata and tissue level expression data via a unified CLI workflow.
It is designed for extensibility using a reusable BaseConnector and Factory pattern, allowing additional databases to be added with minimal changes to the overall architecture.
