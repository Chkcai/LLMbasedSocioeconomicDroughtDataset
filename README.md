📖 Overview
Socioeconomic drought is a complex and widespread hazard. Accurate identification of its onset remains challenging due to the coupled influence of natural and anthropogenic factors. Traditional physical or statistical models often struggle to perfectly simulate the water supply-demand balance across different regions with complex human interventions.

To overcome these limitations, this project proposes a novel framework utilizing Retrieval-Augmented Generation (RAG) technology and Large Language Models (LLMs). By systematically extracting and evaluating unstructured public web data (e.g., government announcements, news reports), we constructed a comprehensive socioeconomic drought database for 368 prefecture-level units across China, spanning from 2010 to 2025. The model performs consistently across diverse economic contexts, achieving an accuracy of 0.92 and an F1-score of 0.91.

✨ Key Features
LLM + RAG Framework: Integrates the Bocha AI Search engine with Alibaba's Qwen3-Max LLM to efficiently mine and analyze massive unstructured text data.

Strict Judgment Logic & Evidence Traceability: The framework systematically evaluates retrieved texts to explicitly branch into "socioeconomic drought occurred" or "socioeconomic drought not occurred" outcomes. When a drought is identified, the model outputs specific webpage links as supporting evidence for manual verification.

High-Value Bilingual Dataset: Provides a comprehensive bilingual (Chinese and English) database recording 2,299 distinct socioeconomic drought events, filling the critical gap where existing databases predominantly focus only on meteorological, hydrological, or agricultural droughts.

📂 Repository Structure
China_Socioeconomic_Drought_Database(2010-2025).xlsx:The socioeconomic drought identification results for 368 prefecture-level cities in China from 2010 to 2025. Includes the identified year, city, model results, supporting webpage links, and manual review results. Due to language limitations on the internet, the supporting webpage links are in Chinese. For the manual review results, 1=TP, 2=FP from engineering and other reasons (FP), 3=FP from LLM hallucination, 4=FN from LLM hallucination, 0=TN.
LLMSocioeconomicDroughtIdentificationModel.yml:The Socioeconomic drought identification model based on RAG and LLM. The code is developed based on Dify platform.
RF_train.m: The code for training the RF model in our paper. The code is developed based on Matlab.
RF_train_data.mat: The data for training the RF model in our paper.
RF_trained_model.mat: The trained RF model in our paper.
