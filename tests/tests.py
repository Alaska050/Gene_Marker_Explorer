"""
Unit tests for the GeneMarker Explorer connectors.
"""

import pytest

from ..connectors.ensembl import EnsemblConnector
from ..connectors.hpa import HPAConnector

class TestEnsemblConnector:
    """Tests for the Ensembl Connector."""
    @pytest.fixture
    def connector(self):
        """Create an EnsemblConnector instance."""
        return EnsemblConnector()

    def test_build_url_CD3D(self, connector):
        """Test URL construction for CD3D gene symbol lookup."""
        url = connector._build_url("CD3D")
        assert url == "https://rest.ensembl.org/xrefs/symbol/homo_sapiens/CD3D"

    def test_build_url_EGFR(self, connector):
        """Test URL construction for EGFR gene symbol lookup."""
        url = connector._build_url("EGFR")
        assert url == "https://rest.ensembl.org/xrefs/symbol/homo_sapiens/EGFR"

    def test_CD3D_returns_correct_value(self, connector):
        """Verify Ensembl returns structured and accurate metadata for CD3D."""
        gene_metadata = connector.get_gene_metadata("CD3D")
        assert gene_metadata.description == 'CD3 delta subunit of T-cell receptor complex [Source:HGNC Symbol;Acc:HGNC:1673]'
        assert gene_metadata.symbol == 'CD3D'
        assert gene_metadata.biotype == 'protein_coding'
        assert gene_metadata.chromosome == '11'
        assert gene_metadata.strand == -1

    def test_EGFR_returns_correct_value(self, connector):
        """Verify Ensembl returns structured and accurate metadata for EGFR."""
        gene_metadata = connector.get_gene_metadata("EGFR")
        assert gene_metadata.description =='epidermal growth factor receptor [Source:HGNC Symbol;Acc:HGNC:3236]'
        assert gene_metadata.symbol == 'EGFR'
        assert gene_metadata.chromosome == '7'
        assert gene_metadata.strand == 1

class TestHPAConnector:
    """Tests for the Human Protein Atlas connector."""

    @pytest.fixture
    def connector(self):
        """Create an HPAConnector instance."""
        return HPAConnector()

    def test_build_url_ENSG00000167286(self, connector):
        """Verify URL construction for CD3D HPA query."""
        url = connector._build_url("ENSG00000167286")
        assert url == "https://www.proteinatlas.org/ENSG00000167286.json"

    def test_build_url_another_example(self, connector):
        """Verify URL construction for EGFR HPA query."""
        url = connector._build_url("ENSG00000146648")
        assert url == "https://www.proteinatlas.org/ENSG00000146648.json"

    def test_ENSG00000167286_returns_correct_value(self, connector):
        """Verify structured HPA expression output for CD3D."""
        data  = connector.get_tissue_expression("ENSG00000167286")
        assert data.gene == "CD3D"
        assert data.ensembl_id == "ENSG00000167286"
        assert isinstance(data.tissue_expression, list)

    def test_ENSG00000146648_returns_correct_value(self, connector):
        """Verify structured HPA expression output for EGFR."""
        data = connector.get_tissue_expression("ENSG00000146648")
        assert data.gene == "EGFR"
        assert data.ensembl_id == "ENSG00000146648"
        assert isinstance(data.tissue_expression, list)
