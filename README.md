# hypothesis-vcf

A [Hypothesis](https://hypothesis.readthedocs.io/en/latest/index.html) strategy for generating VCF (Variant Call Format) files.

## Description

`hypothesis-vcf` is designed to generate VCF files that conform to the VCF specification
([version 4.3](https://samtools.github.io/hts-specs/VCFv4.3.pdf)).
It generates VCFs that are syntactically valid, but which don't have meaningful semantics.

For that reason, the main use case is for testing software that parses VCF or converts VCF
to another format, since Hypothesis will generate examples that exercise many edge cases of
the VCF spec.

In particular, the generated VCFs do *not* have well-known INFO or FORMAT fields, such as `GT`
or `AD`. However, the ability to generate these fields may be added in the future.

## API

The public API consists of just one function: `hypothesis_vcf.vcf`.

## Usage

Generate an example interactively:

```python
>>> from hypothesis_vcf import vcf
>>> print(vcf().example())
##fileformat=VCFv4.3
##FILTER=<ID=PASS,Description="All filters passed">
##source=hypothesis-vcf-0.1.dev2+g32cb4a6
##contig=<ID=C>
##INFO=<ID=Jw,Type=Float,Number=1,Description="INFO,Type=Float,Number=1">
##FORMAT=<ID=zS,Type=Integer,Number=3,Description="FORMAT,Type=Integer,Number=3">
##FORMAT=<ID=ky,Type=String,Number=A,Description="FORMAT,Type=String,Number=A">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
C	87	.	NCNN	CCCTTTCTCNCAGGNA,ACGCCAGTAATCGCGCNNAAAATAAGT,GNTAT	.	.	.
C	251	vRIinp	GGAATGGNTNTNNTCCA	AA,CCGTNATNAA,GAG	.	.	Jw=0.0
```

Generate examples in unit tests:

```python
from hypothesis import given
from hypothesis_vcf import vcf

@given(vcf_string=vcf())
def test_vcf(vcf_string):
    assert vcf_string.startswith("##fileformat=VCF")
```