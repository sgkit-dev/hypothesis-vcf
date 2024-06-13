import pysam
from hypothesis import HealthCheck, given, note, settings

from hypothesis_vcf import vcf


# simple test from README
@given(vcf_string=vcf())
def test_vcf(vcf_string):
    assert vcf_string.startswith("##fileformat=VCF")


# Make sure POS starts at 1, since CSI indexing doesn't seem to support
# zero-based coordinates (even when passing zerobased=True to pysam.tabix_index below)
@given(vcf_string=vcf(min_pos=1))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
def test(tmp_path, vcf_string):
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
