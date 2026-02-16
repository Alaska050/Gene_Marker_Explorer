import pytest

from ..connectors.ensembl import EnsemblConnector
from ..connectors.hpa import HPAConnector

class TestEnsemblConnector:
    """Tests for the Ensembl API connector."""
    @pytest.fixture
    def connector(self):
        """Create an EnsemblConnector instance."""
        return EnsemblConnector()

    def test_build_url_CD3D(self, connector):
        """Test URL construction for gene symbol lookup."""
        url = connector._build_url("CD3D")
        assert url == "https://rest.ensembl.org/xrefs/symbol/homo_sapiens/CD3D"

    def test_build_url_EGFR(self, connector):
        """Test URL construction for gene symbol lookup."""
        url = connector._build_url("EGFR")
        assert url == "https://rest.ensembl.org/xrefs/symbol/homo_sapiens/EGFR"

    def test_CD3D_returns_correct_value(self, connector):
        gene_metadata = connector.get_gene_metadata("CD3D")
        assert gene_metadata.description == 'CD3 delta subunit of T-cell receptor complex [Source:HGNC Symbol;Acc:HGNC:1673]'
        assert gene_metadata.symbol == 'CD3D'
        assert gene_metadata.biotype == 'protein_coding'

    def test_EGFR_returns_correct_value(self, connector): # Alaska to do another one ...
        gene_metadata = connector.get_gene_metadata("EGFR")
        assert gene_metadata.description == 'CD3 delta subunit of T-cell receptor complex [Source:HGNC Symbol;Acc:HGNC:1673]'

class TestHPAConnector:
    """Tests for the Human Protein Atlas connector."""

    @pytest.fixture
    def connector(self):
        """Create an HPAConnector instance."""
        return HPAConnector()

    def test_build_url_ENSG00000167286(self, connector):
        """Test URL construction for HPA query."""
        url = connector._build_url("ENSG00000167286")
        assert url == "https://www.proteinatlas.org/ENSG00000167286.json"

    def test_build_url_another_example(self, connector):# for alaska to do another example ...
        """Test URL construction for HPA query."""
        url = connector._build_url("ENSG00000167286")
        assert url == "https://www.proteinatlas.org/ENSG00000167286.json"

    def test_ENSG00000167286_returns_correct_value(self, connector):
         tissue_expression = connector.get_tissue_expression("ENSG00000167286")
         assert tissue_expression.gene == 'correct value ... '
         assert tissue_expression.ensembl_id == 'correct value ... '
         assert tissue_expression.gene_description == 'correct value ... '

    def test_CD3D_returns_correct_value(self, connector):  # Alaska to do another one ...
        tissue_expression = connector.get_tissue_expression("another example ... ")
        assert tissue_expression.gene == 'correct value ... '
        assert tissue_expression.ensembl_id == 'correct value ... '
        assert tissue_expression.gene_description == 'correct value ... '