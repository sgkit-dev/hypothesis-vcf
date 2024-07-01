import re

import pysam
from hypothesis import HealthCheck, given, note, settings
from hypothesis.strategies import data

from hypothesis_vcf import vcf
from hypothesis_vcf.strategies import (
    RESERVED_FORMAT_KEYS,
    RESERVED_INFO_KEYS,
    Field,
    genotypes,
    vcf_field_keys,
    vcf_fields,
    vcf_values,
)


@given(data=data())
def test_vcf_field_keys(data):
    info_field_key = data.draw(vcf_field_keys("INFO"))
    assert info_field_key not in RESERVED_INFO_KEYS
    format_field_key = data.draw(vcf_field_keys("FORMAT"))
    assert format_field_key not in RESERVED_FORMAT_KEYS


@given(data=data())
def test_info_fields(data):
    field = data.draw(vcf_fields("INFO", max_number=3))
    assert field.category == "INFO"
    assert field.vcf_number != "G"
    if field.vcf_type == "Flag":
        assert field.vcf_number == "0"
    else:
        assert field.vcf_number != "0"


@given(data=data())
def test_format_fields(data):
    field = data.draw(vcf_fields("FORMAT", max_number=3))
    assert field.category == "FORMAT"
    assert field.vcf_type != "Flag"
    assert field.vcf_number != "0"


@given(data=data())
def test_genotypes(data):
    alleles = 3
    ploidy = 2
    gt = data.draw(genotypes(alleles=alleles, ploidy=ploidy))
    allele_index_strs = re.split("[/|]", gt)
    assert len(allele_index_strs) == ploidy
    allele_indexes = [int(idx) if idx != "." else None for idx in allele_index_strs]
    assert all(0 <= idx < alleles for idx in allele_indexes if idx is not None)


@given(data=data())
def test_vcf_values(data):
    field = Field("INFO", "I1", "Integer", "1")
    values = data.draw(vcf_values(field, max_number=3, alt_alleles=1, ploidy=2))
    assert values is not None
    assert len(values) == 1
    assert values[0] is None or isinstance(values[0], int)


# simple test from README
@given(vcf_string=vcf())
def test_vcf(vcf_string):
    assert vcf_string.startswith("##fileformat=VCF")


# Make sure POS starts at 1, since CSI indexing doesn't seem to support
# zero-based coordinates (even when passing zerobased=True to pysam.tabix_index below)
@given(vcf_string=vcf(min_pos=1))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_vcf_parsing_with_pysam(tmp_path, vcf_string):
    note(f"vcf:\n{vcf_string}")

    # Write VCF to a file
    path = tmp_path / "input.vcf"
    with open(path, "w") as f:
        f.write(vcf_string)

    # Check we can index the VCF without error
    # Use CSI since POS can exceed range supported by TBI
    # (this also compresses the input file)
    pysam.tabix_index(str(path), preset="vcf", force=True, csi=True)

    # Check that pysam can parse the VCF without error
    vcf_in = pysam.VariantFile(tmp_path / "input.vcf.gz")
    vcf_out = pysam.VariantFile("-", "w", header=vcf_in.header)
    for variant in vcf_in.fetch():
        vcf_out.write(variant)
