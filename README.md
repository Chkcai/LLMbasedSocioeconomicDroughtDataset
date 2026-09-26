# A Human-Verified Database of Reported Socioeconomic Drought Impacts in China (2010–2025)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22808353.svg)](https://doi.org/10.5281/zenodo.22808353)

## 📖 Overview

Socioeconomic drought is a complex and widespread hazard, yet its impacts remain poorly archived and lack a standardized observation system. This repository accompanies a human-verified database of **reported socioeconomic drought impacts for 368 prefecture-level research units in China, 2010–2025** (5,888 unit-year records; 2,299 verified events).

The records were produced by a **human-in-the-loop framework** that couples a web search engine (Bocha AI Search) with a retrieval-augmented large language model (Qwen3-Max, Alibaba Cloud) to identify publicly reported socioeconomic drought impacts from Chinese web sources, followed by **independent manual verification of every record** against government bulletins, the *Yearbook of Meteorological Disasters in China*, and targeted web searches.

The primary, citable archive of the database is on **Zenodo**: [https://doi.org/10.5281/zenodo.22808353](https://doi.org/10.5281/zenodo.22808353) (this DOI always resolves to the latest version). This GitHub repository serves as a mirror of the database and hosts the complete source code and the verification sample.

## 📂 Repository Structure

| File | Description |
|---|---|
| `China_Socioeconomic_Drought_Database(2010-2025)_v4.xlsx` | The bilingual database: 17 worksheets (1 Introduction + 16 annual sheets), 5,888 unit-year records. Fields include Province (CN/EN), Research unit (CN/EN), Model Results (CN/EN), Supporting Webpage Links (CN), Manual Review Results (codes 0–4), and four multi-label Manifestation fields. Manual review codes: 1 = true positive, 2 = false positive (engineering or other non-drought causes), 3 = false positive (LLM hallucination), 4 = false negative recovered by manual review, 0 = true negative. |
| `LLMSocioeconomicDroughtIdentificationModel.yml` | Module (i): the retrieval-augmented identification workflow (Dify platform export), coupling Bocha AI Search with the Qwen3-Max LLM for binary discrimination. |
| `manifestation_type_classification.py` | Module (ii): multi-label keyword-matching classification of manifestation types (supply-side impacts, demand-side impacts, emergency response, other impacts) from the supporting report texts. |
| `SPEI_conditional_probability.py` | Module (iii): computes the conditional probability of a verified event given the SPEI drought class (GB/T 20481-2017), with 95% Wilson score intervals. |
| `manifestation_verification_sample50.xlsx` | The 50-sample verification set used for the blind review of manifestation type labels (agreement rate 93.0%). |

## ⚙️ Requirements

- Module (i) runs on the [Dify](https://dify.ai/) platform and requires **your own API keys** for Bocha AI Search and Alibaba Cloud (Qwen3-Max). No API keys are included in this repository.
- Modules (ii) and (iii) require Python 3.13 with NumPy and pandas, and run on a standard desktop CPU.

## 📑 Citation

If you use this database, please cite the Zenodo archive:

> Cai, C., Wang, J., Zhao, Y., Niu, Z., Ren, S., Huang, Y., Jin, Y., Wang, H., Wang, J. & Shen, X. A human-verified database of reported socioeconomic drought impacts for 368 prefecture-level units in China, 2010–2025. *Zenodo*. https://doi.org/10.5281/zenodo.22808353 (2026).

A companion Data Descriptor describing this database is under review at *Scientific Data*.

## 📄 License

- **Code** in this repository is released under the [MIT License](LICENSE).
- **Data** (`China_Socioeconomic_Drought_Database(2010-2025)_v4.xlsx` and `manifestation_verification_sample50.xlsx`) are released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), as archived on Zenodo.

## ✉️ Contact

Chenkai Cai — chkcai@outlook.com
