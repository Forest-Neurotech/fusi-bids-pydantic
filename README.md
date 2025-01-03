# fusi-bids-pydantic

[![Build status](https://img.shields.io/github/actions/workflow/status/Forest-Neurotech/fusi-bids-pydantic/test.yml?branch=main)](https://github.com/Forest-Neurotech/fusi-bids-pydantic/actions/workflows/test.yml?query=branch%3Amain)
[![Supported Python versions](https://img.shields.io/badge/python-3.9_%7C_3.10_%7C_3.11_%7C_3.12_%7C_3.13-blue?labelColor=grey&color=blue)](https://github.com/Forest-Neurotech/fusi-bids-pydantic/blob/main/pyproject.toml)
[![License](https://img.shields.io/github/license/Forest-Neurotech/fusi-bids-pydantic)](https://img.shields.io/github/license/Forest-Neurotech/fusi-bids-pydantic)

Pydantic model for fUSI-BIDS extension proposal (BEP) sidecar JSON schema

- **Github repository**: <https://github.com/Forest-Neurotech/fusi-bids-pydantic/>


### Installation

Clone the repository:

```bash
git clone https://github.com/Forest-Neurotech/fusi-bids-pydantic.git
cd fusi-bids-pydantic
```

For general usage, install the package:

```bash
pip install -e .
```

Or for development, install the environment and the pre-commit hooks:

```bash
make install
```

### Usage

```python
from fusi_bids_pydantic import FUSISidecar

example_sidecar_data = {
    "TaskName": "example_task",
    "RepetitionTime": 1.5,
    "Manufacturer": "example_manufacturer",
}
sidecar = FUSISidecar.model_validate(example_sidecar_data)
# Warns about missing RECOMMENDED fields
```
