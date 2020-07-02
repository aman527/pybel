# -*- coding: utf-8 -*-

"""Tests for the jsonschema node validation."""

import unittest

import pybel.dsl
from pybel.schema import is_valid_node
from tests.schema_constants import (
    NAMESPACE, NAME, IDENTIFIER, BLANK_ABUNDANCE,
    PROTEIN, GENE, PROTEIN_SUB, PROTEIN_MOD, FRAGMENT, GENE_MOD
)


class TestSchema(unittest.TestCase):
    """Tests for the jsonschema node validation."""

    def test_pure_abundances(self):
        """Test validating abundance nodes."""
        self.assertTrue(is_valid_node(PROTEIN))
        self.assertTrue(is_valid_node(GENE))

        abundance = pybel.dsl.Abundance(namespace=NAMESPACE, name=NAME, identifier=IDENTIFIER)
        self.assertTrue(is_valid_node(abundance))

    def test_variant_abundances(self):
        """Test validating abundance nodes with variants."""
        gmod = GENE.with_variants(GENE_MOD)
        self.assertTrue(is_valid_node(gmod))

        psub = PROTEIN.with_variants(PROTEIN_SUB)
        self.assertTrue(is_valid_node(psub))

        pmod = PROTEIN.with_variants(PROTEIN_MOD)
        self.assertTrue(is_valid_node(pmod))

        frag = PROTEIN.with_variants(FRAGMENT)
        self.assertTrue(is_valid_node(frag))

    def test_matching_variants(self):
        """Test catching invalid abundance/variant pairs, e.g. ProteinModification on a Gene."""
        invalid_gmod = PROTEIN.with_variants(GENE_MOD)
        self.assertFalse(is_valid_node(invalid_gmod))

        invalid_psub = GENE.with_variants(PROTEIN_SUB)
        self.assertFalse(is_valid_node(invalid_psub))

        invalid_pmod = GENE.with_variants(PROTEIN_MOD)
        self.assertFalse(is_valid_node(invalid_pmod))

        invalid_frag = GENE.with_variants(FRAGMENT)
        self.assertFalse(is_valid_node(invalid_frag))

    def test_fusions(self):
        """Test validating fusion nodes."""
        protein = pybel.dsl.Protein(namespace=NAMESPACE, name=NAME,
                                    identifier=IDENTIFIER)
        enum_fusion_range = pybel.dsl.EnumeratedFusionRange("r", 1, 79)
        missing_fusion_range = pybel.dsl.MissingFusionRange()
        fusion_node = pybel.dsl.FusionBase(protein, protein,
                                           range_5p=enum_fusion_range,
                                           range_3p=missing_fusion_range)
        self.assertTrue(is_valid_node(fusion_node))

    def test_list_abundances(self):
        """Test validating list abundance nodes."""
        complex_abundance = pybel.dsl.ComplexAbundance([GENE, PROTEIN], namespace=NAMESPACE,
                                                       name=NAME, identifier=IDENTIFIER)
        composite_abundance = pybel.dsl.CompositeAbundance([PROTEIN, complex_abundance])
        self.assertTrue(is_valid_node(complex_abundance))
        self.assertTrue(is_valid_node(composite_abundance))

    def test_reaction(self):
        """Test validating a reaction node."""
        node = pybel.dsl.Rna(namespace=NAMESPACE, name=NAME, identifier=IDENTIFIER)
        node_list = [node, node, node]
        rxn = pybel.dsl.Reaction(reactants=node_list, products=node_list)
        self.assertTrue(is_valid_node(rxn))

    def test_invalid_abundances(self):
        """Test that invalid abundances are caught."""
        missing_fn = BLANK_ABUNDANCE.copy()
        missing_fn.pop("function")
        self.assertFalse(is_valid_node(missing_fn))

    def test_invalid_psub(self):
        """Test that invalid protein substitutions are caught."""
        missing_hgvs = dict(PROTEIN_SUB)
        # Remove the required "hgvs" property
        missing_hgvs.pop("hgvs")
        protein = BLANK_ABUNDANCE.copy()
        protein["function"] = "Protein"
        protein["variants"] = [missing_hgvs]
        self.assertFalse(is_valid_node(protein))


if __name__ == '__main__':
    unittest.main()
